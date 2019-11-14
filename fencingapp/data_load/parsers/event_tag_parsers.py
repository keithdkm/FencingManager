'''
Parsers to extract event data from tags 
scraped by beautiful soup
'''
import logging

from re import findall
from collections import namedtuple
from datetime import datetime as dt


from fencingapp.data_load.locators.tournament_locators import TournamentSummaryLocator
from fencingapp.models import Event

Eventtuple = namedtuple('Event',Event.__table__.columns.keys())
    # pulled field names directly from db schema   
    # currently ['id_', 'name', 'type', 'weapon', 'gender', 'abbreviation',
    #  'count,'rating','tournament_id', 'start', 'status', 'created_on', 'updated_on']
logger = logging.getLogger('fencing')

def date_range_split(date_range_string):
    '''
    formats readable date range string into datetime format start and finish dates
    '''
    patterns = ('(\d{1,2})[ |,]', '[a-zA-Z]{3}','\d{4}') #pattern matches for date string components
    days,months,year = [[a.strip() for a in findall(p,date_range_string)] for p in patterns]
    # extract date string components from date string
    start = dt.strptime(days[0]+months[0]+year[0],'%d%b%Y')
    finish   = dt.strptime(days[-1]+months[-1]+year[0],'%d%b%Y')
    return start,finish

class EventSummaryTagParser:
    '''
    Accepts an HTML tag containing  list of events from a tournament, 
    returns a named tuple with summary event data - 
    Name,Type e.g. Junior, weapon, gender, abbreviation,
    and USFA event id, number of entrants.
    '''

    # TODO rewrite to split parsing into separate methods 

    gender = {  "0" : ("Mixed", "Mixed", "Mx"),
                "4" : ("Women's","Women","W"),
                "3" : ("Men's","Men","M")}
    weapon = {  "1" : ("Foil","F"),
                "2" : ("Epee","E"),
                "3" : ("Saber","S")}


    def __init__(self,parent,tourn_id):  # parent is the Beautiful Soup tag of a single tournament

        
        self.parent = parent


        self.details = parent.stripped_strings
        # parent.stripped_strings is a generator presenting
        # e.g.('Division I Men’s Epee (DV1ME)', '8:00am Close of Registration', 'Entrants', '277')
        self.names = next(self.details).split(' (')
        time_ = next(self.details).split(" ")[0]
        if time_== "Entrants" or time_== "Possible":  #If events have not yet been scheduled, 
            time_="12:00am"    # set their time to midnight
        year_= list(parent.parents)[-1].select_one('span.lead').text.split(', ')[-1]
        temp_start = next(parent.parent.stripped_strings) + " " + time_ + " " + year_
        
        self.id_ = self.parent['data-event_id']
        self.name = self.names[0]
        self.type = " ".join(self.name.split(" ")[:-2])
        self.abbreviation = self.names[-1][:-1]
        self.count = int(list(self.details)[-1])
        self.start = dt.strptime(temp_start,"%A, %B %d %I:%M%p %Y")
        self.tourn_id = tourn_id
        rating = self.parent.select_one('span.link')
        if rating:
            rating=rating.text.strip()
            if rating=="Possible Not Rated":
                self.rating = 'NR'
            else:
                self.rating = rating.split(" ")[-1]
        else:
            self.rating = None

    def __repr__(self):
        return f'{self.rating}, {self.count} competitors with code {self.id_}'

  

    @property
    def all(self):
        
        return Eventtuple(id_=self.id_,
                     name=self.name, 
                     type=self.type, 
                     weapon=self.weapon[self.parent['data-weapon']][0], 
                     gender=self.gender[self.parent['data-gender']][1], 
                     abbreviation=self.abbreviation,
                     count=self.count,
                     rating=self.rating,
                     tournament_id=self.tourn_id, 
                     start=self.start, 
                     status="",
                     created_on="",
                     updated_on="")
