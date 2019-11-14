'''
Parsers to extract tournament data from html tags
'''
import logging

from re import findall
from collections import namedtuple
from datetime import datetime as dt

from fencingapp.models import Tournament
from fencingapp.data_load.locators.tournament_locators import TournamentSummaryLocator

Tournament = namedtuple('Tournament',Tournament.__table__.columns.keys()
                        )


Location = namedtuple('Location',[
                                 'Venue',
                                 'City',
                                 'State'
                                 ]
                      )

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

class TournamentSummaryParser:
    '''
    Accepts an Beautiful Soup tag for tournament in list of tournaments from USFA website, 
    and returns a named tuple with summary tournament data - 
    Name,Date, (Venue,City,State) and USFA tournament Code.
    '''

    def __init__(self,parent):  # parent is the html tag of a single tournament on 
        self.parent = parent    # the USFA tournament list page

    def __repr__(self):
        return f'{self.name} on {self.dates} at {self.location} with code {self.USFA_ID}'

    @property
    def dates(self): #extracts tournament dates
        '''
        Locates date string and parses out datetime objects for start and finish date
        '''
        try:
            locator = TournamentSummaryLocator.DATES
            dates_ = self.parent.select_one(locator).text.strip()
            start,finish = date_range_split(dates_)
        except Exception as e:
            logger.warning (f'Parsing of tournament date data failed with . Date is',{str(e)} ,{dates_})
            start = finish = dt
        finally:
            logger.debug('Parsed %s' , dates_)
            return (start,finish)


    @property
    def name(self): #extracts tournament name
       try:
           locator = TournamentSummaryLocator.NAME
           tournament_ = self.parent.select_one(locator).string.strip()
           
       except Exception as e:
           logger.warning (f'Parsing of tournament name data failed with %s',str(e))
           tournament_ = 'TBD'
       finally:
        #    logger.debug ('Parsed %s', unicode(tournament_,'unicode-escape') )
           return (tournament_)

    @property
    def USFA_ID(self): #extracts tournament web ID(unique)
       try:
           locator = TournamentSummaryLocator.CODE
           code_ = self.parent.select_one(locator)['href'].split('/')[-1]
       except Exception as e:
           logger.warning (f'Parsing of tournament code data failed with %s',str(e))
           code_ = '0000'
       finally:
           logger.debug('Parsed %s',code_)
           return (code_)

    @property
    def location(self): #extracts tournament location
       try:
           locator = TournamentSummaryLocator.LOCATION
           location = ','.join(s.strip()
                                for s in self.parent.select(locator)[2].contents
                                if isinstance(s,str) ).split(',')         #strips line breaks

           if len(location)  == 0:   # Unusual - No location data provided
               venue = city = state = 'TBD'
           elif len(location) == 2:     # No venue provided
               city,state = location
               venue = 'TBD'
           elif len(location)==3:     # regular format
               venue,city,state = location
           else: (venue,city,state) = ','.join(location[:-2]),location[-2],location[-1]
           state = state[1:]           # unusual - venue has commas in name
       except Exception as e:
           logger.warning ('Parsing of tournament location data with %s. Failed with %s',self.name,str(e))
           venue = city = state = 'Not Found'
       finally:
           location_ = Location(venue ,city,state)
           logger.debug('Parsed %s', location_ )
           return (location_)

    @property
    def all(self):
        return Tournament(self.USFA_ID,     #id_
                          None,             #ft_id
                          *self.location,   #venue,city,state
                          self.name or None,#name
                          None,             #opens
                          None,             #closes
                          None,             #withdrawal
                          *self.dates,      #start, end
                          None,             #region
                          None,             #type
                          None,             #season_id
                          None,             #status
                          None,             #created_on
                          None              #updated
                         
                          )

class TournamentDetailParser():
    ''' 
    Accepts Beautiful Soup tag of tournament detail page and returns the 
    registration dates as a tuple
    '''
    
    def __init__(self,tag_):
        self.parent = tag_

    @property
    def registration_dates(self): #extracts tournament registration deadline dates

        try:
           dates_locator = TournamentSummaryLocator.REG_DATES  # CSS selector of tournament dates
           
           date_dict = {e[0]:e[1] for e in [[s for s in t.stripped_strings] 
               for t in self.parent.select(dates_locator)]}  # create a dictionary of all the tournament
                                                             # times and dates
                                                             # soup select returns a list with elements
                                                             # in this format
                                                             # ['Registration Opens', 'Aug 28, 2019', '12:00am']
                
           open_date,close_date,withdraw_date=[   
               dt.strptime(date_dict.get(t,"Jan 1, 1900"),'%b %d, %Y') for t in [   # convert text date into actual date
                   'Registration Opens','Entry Deadline','Withdrawal Deadline']] # list of dates to be returned

        except Exception as e:
            logger.warning (f'Parsing of tournament deadline date data failed for {self.parent.select_one("title").text}')
            open_date=close_date=withdraw_date = None
        finally:
            # logger.debug('Parsed %s' , open_date)
        
            return (open_date,close_date,withdraw_date)