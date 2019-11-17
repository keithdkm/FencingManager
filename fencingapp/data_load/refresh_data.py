import random
import time
from datetime import datetime as dt
from datetime import timedelta

from fencingapp.data_load.members import load_members_to_db_from_csv
from fencingapp.data_load.events import load_events_to_db_from_USFA
from fencingapp.data_load.tournaments import load_tournaments_from_USFA
from fencingapp import db, create_app
from fencingapp.models import Season,Tournament,Event,Member
from sqlalchemy import func

# create application context for job to run in
app = create_app()
app.app_context().push() 


# Refresh Members to get latest ratings data
# TODO improve logic to set this season
print('Loading Seasons')
st = dt.strptime

this_season = Season(st("08/01/2019","%m/%d/%Y"),st("07/31/2020","%m/%d/%Y"))
last_season = Season(st("08/01/2018","%m/%d/%Y"),st("07/31/2019","%m/%d/%Y"))
next_season = Season(st("08/01/2020","%m/%d/%Y"),st("07/31/2021","%m/%d/%Y"))
db.session.add_all([this_season,last_season,next_season])
db.session.commit()

# Refresh members every time app runs to get latest fencer ratings
print ('Loading members')
Member.query.delete()
db.session.commit()
# concatenates last year's file with latest downlaod from USFA website
load_members_to_db_from_csv()


# Refresh tournaments if the most recent update was more than 7 days ago
print('starting event load')
MAX_DAYS_SINCE_REFRESH=7
if (Tournament.query.count()==0 or   # if tournament table is empty
    Tournament.query.with_entities(  # or if it hasn't been refreshed in less 7 datas
    func.max(Tournament.updated_on))[0][0]<dt.utcnow()-timedelta(days=MAX_DAYS_SINCE_REFRESH)):
    Tournament.query.filter(Tournament.start>dt.now()).delete()  #<- deletes data for all tournaments that haven't started
    db.session.commit()
    load_tournaments_from_USFA(this_season,whole_season=False,to_csv=False,refresh_table=True) 

print('Tournament refresh complete')
# Refresh events

t_list = Tournament.query.filter(Tournament.start>dt.utcnow()) # Select all tournaments that haven't started yet
# model now cascades event deletes from tournament deletes sp they don't have to be deleted here
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

