from datetime import datetime as dt
import random
import pandas as pd
import time
import os
from pathlib import Path


from fencingapp.data_load.scrapers.tournaments import ScrapeTournamentsList,ScrapeTournamentDetails  #
from fencingapp.data_load.URLs.URLs import USFA_URLs

from fencingapp import db
from fencingapp.models import Tournament

def load_tournaments_from_USFA(season,whole_season=True,\
                                to_csv=True,refresh_table=False): 
    ''' retrieves all the tournaments for the requested season from USFA, 
        iterating through pages of results of national tournaments and each of the types
        and returning a list of Tournaments. If whole_season is True, it loads all the 
        tournaments, otherwise it loads tournaments that start after today
    '''
    # TODO rewrite code to season and partial season updates. Currently refreshes all the data.
    # Could probably use current&upcoming filter
    print(f'Season is {season}. Whole season is {whole_season}. refresh table is {refresh_table}')
    REGIONAL_TOURNAMENT_TYPES = {
                             'RJCC': 3,
                             'RCC': 4,
                             'RJC': 5,
                             'ROC':6,}


    regions = [1,1,2,2,2,2,3,3,3,3,3,4,4,4,4,5,5,6,6,6,6,6,6,6,6,2]
    states = ['WA','OR','IL','OH','MO','KS','NJ','MA','NY','PA','CT','UT',\
        'CA','CO','NV','TX','LA','NC','GA','VA','AL','TN','MD','FL','DC','WI']
    REGION_MAP = dict(zip(states,regions))

    def status(tourn_row):  #helper to populate tournament status field based upon date
        if tourn_row['start'] > dt.now():
            return 'Upcoming'
        elif dt.now() > tourn_row['end']:
            return 'Completed'
        else: 
            return 'Underway'
    
    tournament_df = pd.DataFrame()
    season_code = int(dt.strftime(season.end,'%y')) + 30 # search code for each season

    if whole_season:   # season_filter passed as parameter to website to filter results
        season_filter = season_code      # give me the whole season
    else:
        season_filter = 'future&designated='   # give me tournaments that haven't started yet


    # Fetch national tournaments
    tournament_df = ScrapeTournamentsList(
                        USFA_URLs.NATIONAL_TOURNAMENT_SEARCH,
                        search_params = {'filter_by_show': season_filter},
                        tourn_type = "National"
                                         ).tournament_list

    # Fetch regional tournaments
    for type_,type_code in REGIONAL_TOURNAMENT_TYPES.items(): # iterate through tournament types
        tournament_df = pd.concat([tournament_df,
                                   ScrapeTournamentsList(
                                        USFA_URLs.REGIONAL_TOURNAMENT_SEARCH,
                                        search_params ={
                                                     'filter_by_show': season_filter,
                                                     'filter_by_event_type': type_code},
                                        tourn_type = type_
                                                ).tournament_list]
                                 )
        # insert random pause of up to 10 seconds
        event_type_wait = random.uniform(0,10)
        print(f'Finished getting {type_} tournaments for {season}. Waiting {event_type_wait} seconds')
        time.sleep(event_type_wait)

    # Fetch SJCCs, which require a regional search on event_scope. May change in future 
    # if USFA adds SJCC to the list of event(sic - should be tournament type) types, 
    # which would be the more logical way of dealing with SJCCs
    tournament_df = pd.concat([tournament_df,
                               ScrapeTournamentsList(
                                    USFA_URLs.REGIONAL_TOURNAMENT_SEARCH,
                                    search_params ={
                                                 'filter_by_show': season_filter,
                                                 'event_scopes': 'scc'},
                                    tourn_type = 'SJCC'     # tournament type to include in tournament data
                                                    ).tournament_list])
    print(f'Finished getting SJCC tournaments for {season}.')

    if not whole_season: # 
        tournament_df = tournament_df[tournament_df.start>dt.now()]

    #     Populate Region number for Regional Tournaments
    tournament_df['region'] = tournament_df.apply(
        lambda x: REGION_MAP.get(
            x['state'],"Not Found") if
                x.get('type' ,"") in REGIONAL_TOURNAMENT_TYPES else 'NA',axis=1)
       
    # Aggregate Tournament types into a list represented as a string
    type_groups = (tournament_df
                        .groupby('id_')['type']
                        .apply(lambda type: ','.join(type)))

    tournament_df = (tournament_df.drop('type',1)
                        .merge(type_groups,'left','id_')
                        .drop_duplicates('id_')
                                )

    # Populate tournament deadline dates for each tournament
    tournament_df[['opens','closes','withdraw']] = (tournament_df.apply( 
        lambda x: pd.Series(ScrapeTournamentDetails(x['id_']).registration_dates),axis=1))

    # Populate season into season foreign key
    tournament_df['season_id'] = season.id_
    
    # Populate date/time into updated and created fields
    tournament_df['updated_on'] = tournament_df['created_on'] = dt.utcnow()
    
    tournament_df['status'] = tournament_df.apply(status, axis = 1 )


    print('All tournament data retrieved and formatted')

    # generate csv file and/or refresh table 
    if to_csv:
        if not os.path.isdir(os.path.abspath('testing/debug')):
            os.mkdir(os.path.abspath('testing/debug'))
        debug_file_path = os.path.abspath('testing/debug')
        file_ = 'scraped_tournament_'+ str(season.start.year)+'.csv'
        tournament_df.to_csv(Path(debug_file_path,file_))  # DEBUG
    if refresh_table:
        try: 
            print('removing table constraint for bulk insert')
            db.engine.execute(                          # TODO remove hardcoded CONSTRAINT name
                'ALTER TABLE events DROP CONSTRAINT events_tournament_id_fkey')  # drop FK constraint with user table
            db.session.commit()
        except Exception as e:
            print(f"Removing events table constraint failed with {e}")
        else:
            print('constraint successfully removed')
        if whole_season:                      # if whole season being refreshed
            Tournament.query\
                      .filter(Tournament.start>season.start, Tournament.end<season.end)\
                      .delete()               # delete all tournaments in required season
        else:
            Tournament.query\
                      .filter(Tournament.start>dt.now(), Tournament.end<season.end)\
                      .delete()               # deletes data for all tournaments that haven't started
        db.session.commit()                   # commit the delete

        print('Writing tournament data to database')
        tournament_df.to_sql(
            'tournaments',db.engine,if_exists='append',index=False) # write new tournament data to table
        print('wrote tournament records to database, restoring foreign key constraints')

        db.engine.execute(                                          # TODO remove hardcoded CONSTRAINT name
            'ALTER TABLE events\
                 ADD CONSTRAINT events_tournament_id_fkey\
                 FOREIGN KEY(tournament_id) REFERENCES tournaments(id_)')
        db.session.commit()   
    return 
