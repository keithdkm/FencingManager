from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime as dt

from fencingapp.data_load.locators.event_locators import EventSummaryLocator, EventLocators
from fencingapp.data_load.parsers.event_tag_parsers import EventSummaryTagParser
from fencingapp.data_load.URLs.URLs import USFA_URLs

class ScrapeTournamentDetails:
    '''
        Accepts USFA tournament code,
        fetches the  page of results of events, 
        fetches the html tags of each event using BeautifulSoup, 
        calls appropriate parsers to retrieve tagged data and then returns 
        a dataframe of event data.
    '''

    def __init__(self,tourn_id):        
        self.target = USFA_URLs.TOURNAMENT_DETAILS + str(tourn_id)   # target URL
        self.tourn_id = tourn_id
        
        self.html_ = requests.get(self.target ) # retrieve events
        self.soup = BeautifulSoup(self.html_.text,'lxml')

    @property
    def event_list(self):  
        '''
        returns df of all events in tournament
        '''
              
        results = pd.DataFrame( [ 
                    EventSummaryTagParser(tag_,self.tourn_id).all for tag_ in self.soup.select(EventLocators.EVENT_LIST)]
                                    )# parse data  from each individual found tag into a single row
        return results

 

    @property
    def tournament_reg_dates(self):
        '''
        returns tuple containing registration open,registration deadline, 
        and withdrawal deadline
        '''
        
        reg_open,reg_close,withdraw_close=[
            dt.strptime(t,'%b %d, %Y')
                for t in [list(t.parent.parent.stripped_strings)[1]
                    for t in self.soup.select('div div span') 
                        if t.text in
                        [' Registration Opens',' Entry Deadline',' Withdrawal Deadline']]]
        return (reg_open,reg_close,withdraw_close)