import os
import random
import time
from datetime import datetime as dt
from datetime import timedelta

from sqlalchemy import func

from fencingapp import create_app, db
from fencingapp.data_load.events import load_events_to_db_from_USFA
from fencingapp.data_load.members import load_members_to_db_from_csv
from fencingapp.data_load.tournaments import load_tournaments_from_USFA
from fencingapp.models import Event, Member, Season, Tournament

print(f"Current working directory is {os.getcwd()}")


# create application context for job to run in
app = create_app()
app.app_context().push() 


# Refresh Members to get latest ratings data
this_season = Season.query.filter(Season.start<=dt.today(),Season.end>=dt.today()).first()

this_time_last_year = dt.today()-timedelta(days=365)

last_season = Season.query.filter(Season.start<=(this_time_last_year),Season.end>=this_time_last_year).first()

# Refresh members every time app runs to get latest fencer ratings
print ('Loading members')

load_members_to_db_from_csv()

print('Members loaded successfully')

# Refresh tournaments if the most recent update was more than 7 days ago
print('Starting tournament load')

Tournament_table_empty = Tournament.query.count()==0
if Tournament_table_empty:
        db.session.commit()   # removes locks on table
        load_tournaments_from_USFA(this_season,
                                whole_season=True,
                                to_csv=False,
                                refresh_table=True) 
        # load_tournaments_from_USFA(last_season,
        #                         whole_season=True,
        #                         to_csv=False,
        #                         refresh_table=True) 
        
else:
    
    MAX_DAYS_SINCE_TOURNAMENT_REFRESH=0
    Last_date_of_refresh  = db.session.query(db.func.max(Tournament.updated_on)).scalar()
    date_refresh_required_after = dt.utcnow()-timedelta(days=MAX_DAYS_SINCE_TOURNAMENT_REFRESH)

    Tournament_data_stale = Last_date_of_refresh < date_refresh_required_after 
                              
    if Tournament_data_stale:
         # if tournament table is empty or if it hasn't been refreshed
        db.session.commit()    # removes locks on table
        load_tournaments_from_USFA(this_season,
                                    whole_season=True,
                                    to_csv=False,
                                    refresh_table=True) 
    print('Tournament refresh complete')

# Refresh events

t_list = Tournament.query.filter(Tournament.start>dt.utcnow()) # Select all tournaments that haven't started yet
# model now cascades event deletes from tournament deletes sp they don't have to be deleted here
print('Refreshing event info for all future tournaments')
for t in t_list:
    Event.query.filter_by(tournament_id=t.id_).delete() # delete events for each tournament
    db.session.commit()
    load_events_to_db_from_USFA(t.id_,to_csv=False,refresh_table=True)
    event_wait = random.uniform(0,10)
    print(f'Finished getting events for {t.name}. Waiting {event_wait} seconds')
    time.sleep(event_wait)

print('Event refresh complete')




#########################################################################
# old data refresh code. 

# # season1920 = Season( start=dt.strptime('8-1-19', "%m-%d-%y"),
# #                      end=dt.strptime('7-31-20',"%m-%d-%y"))
# # season1819 = Season( start=dt.strptime('8-1-18', "%m-%d-%y"),
# #                      end=dt.strptime('7-31-19',"%m-%d-%y"))


# # session.add(season1920)
# # session.add(season1819)
# # session.commit()

# this_season = (session.query(Season)
#                       .filter(Season.start==dt.strptime('8-1-19', "%m-%d-%y"))
#                       .first())
# last_season = (session.query(Season)
#                        .filter(Season.start==dt.strptime('8-1-18',"%m-%d-%y"))
#                        .first())
# data_file_path = Path(r'~\OneDrive\Documents\Fencing\data\\').expanduser()   #  location of membership files



# logging.basicConfig(
#     format = '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#     datefmt = '%Y-%m-%d %H:%M:%S',
#     level = logging.DEBUG,
#     filename = Path('logs/fencing_app_log.txt'))


# logger = logging.getLogger('fencing')
