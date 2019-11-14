from datetime import datetime as dt
import random
import pandas as pd
import time
from pathlib import Path

from fencingapp.data_load.scrapers.tournaments import ScrapeTournamentsList,ScrapeTournamentDetails  #
from fencingapp.data_load.URLs.URLs import USFA_URLs

from fencingapp import db
from fencingapp.models import Tournament

def load_tournaments_from_USFA(season,whole_season=True,to_csv=True,refresh_table=False):  #scrapes and parses html tournament summary data from USFA 
    ''' retrieves all the tournaments for the current season from USFA, 
        iterating through pages of results
         of national tournaments and each of the types and returning a list of Tournaments.
         If whole_season is True, ti loads all the tournaments, otherwise it loads tournaments that 
         start after today
    '''

    REGIONAL_TOURNAMENT_TYPES = {
                             'RJCC': 3,
                             'RCC': 4,
                             'RJC': 5,
                             'ROC':6,}


    regions = [1,1,2,2,2,2,3,3,3,3,3,4,4,4,4,5,5,6,6,6,6,6,6,6,6,2]
    states = ['WA','OR','IL','OH','MO','KS','NJ','MA','NY','PA','CT','UT','CA','CO','NV','TX','LA','NC','GA','VA','AL','TN','MD','FL','DC','WI']
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

    # Fetch national tournaments
    tournament_df = ScrapeTournamentsList(
                        USFA_URLs.NATIONAL_TOURNAMENT_SEARCH,
                        search_params = {'filter_by_show': season_code},
                        tourn_type = "National"
                                         ).tournament_list

    # Fetch regional tournaments
    for type_,type_code in REGIONAL_TOURNAMENT_TYPES.items(): # iterate through tournament types
        tournament_df = pd.concat(
           [tournament_df,ScrapeTournamentsList(
               USFA_URLs.REGIONAL_TOURNAMENT_SEARCH,
                   search_params ={
                                'filter_by_show': season_code,
                                'filter_by_event_type': type_code},
                   tourn_type = type_
                                               ).tournament_list]
                                 )
        # insert random pause of up to 10 seconds
        event_type_wait = random.uniform(0,10)
        print(f'Finished getting {type_} events for {season}. Waiting {event_type_wait} seconds')
        time.sleep(event_type_wait)

    # Fetch SJCCs, which require a regional search on event_scope. May change in future 
    # if USFA adds SJCC to the list of event(sic - should be tournament type) types, 
    # which would be the more logical way of dealing with SJCCs
    tournament_df = pd.concat([tournament_df,ScrapeTournamentsList(
               USFA_URLs.REGIONAL_TOURNAMENT_SEARCH,
                   search_params ={
                                'filter_by_show': season_code,
                                'event_scopes': 'sjcc'},
                   tourn_type = 'SJCC'
                                               ).tournament_list])

    if not whole_season: # 
        tournament_df = tournament_df[tournament_df.start>dt.now()]

    # https://member.usafencing.org/search/tournaments/regional?search=&filter_by_region=all&filter_by_weapon=&filter_by_gender=all&event_scopes=sjcc&filter_by_type=&filter_by_event_type=&filter_by_show=future&designated=
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

    # Populate tournament deadline
    tournament_df[['opens','closes','withdraw']] = (tournament_df.apply( 
        lambda x: pd.Series(ScrapeTournamentDetails(x['id_']).registration_dates),axis=1))

    # Populate season into season foreign key
    tournament_df['season_id'] = season.id_
    
    # Populate date/time into updated and created fields
    tournament_df['updated_on'] = tournament_df['created_on'] = dt.utcnow()
    
    tournament_df['status'] = tournament_df.apply(status, axis = 1 )

    if to_csv:
        file_ = 'scraped_tournament_'+str(season.start.year)+'.csv'
        debug_file_path = Path(r'~\OneDrive\Documents\Data Science\Python\Data Science Projects\Escrime\testing\debug\\').expanduser()   #  location of log files
        tournament_df.to_csv(Path(debug_file_path,file_))  # DEBUG
    if refresh_table:
        tournament_df.to_sql('tournaments',db.engine,if_exists='append',index=False)
    
    return 
