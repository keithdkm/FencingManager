from datetime import datetime as dt
import pandas as pd

from pathlib import Path

from fencingapp import db
from fencingapp.models import Tournament
from fencingapp.data_load.scrapers.events import ScrapeTournamentDetails  #
from fencingapp.data_load.URLs.URLs import USFA_URLs



def load_events_to_db_from_USFA(tournament,to_csv=True,refresh_table=False):
    '''
    Retrieves all the events for a tournament and produces a csv and/or updates 
    the database
    '''

    event_df = ScrapeTournamentDetails(tournament).event_list

    if to_csv:
        file_ = 'scraped_event_df_'+ str(tournament)+ '.csv'
        logging_file_path = Path(r'~\OneDrive\Documents\Data Science\Python\Data Science Projects\Escrime\testing\debug\\').expanduser()   #  location of log files
        event_df.to_csv(Path(logging_file_path,file_))  # DEBUG
    # Populate date/time into updated and created fields
    if refresh_table:
        event_df['updated_on'] = event_df['created_on'] = dt.utcnow()
        event_df.to_sql('events',db.engine,if_exists='append',index=False)
    return


