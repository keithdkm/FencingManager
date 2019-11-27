import logging
from itertools import count
import requests
import pandas as pd
import random
import time
from lxml import html
from bs4 import BeautifulSoup

from fencingapp.data_load.locators.tournament_locators import TournamentLocators
from fencingapp.data_load.parsers.tournamentparsers import TournamentSummaryParser,TournamentDetailParser
from fencingapp.data_load.URLs.URLs import USFA_URLs


class ScrapeTournamentsList:
    '''
        accepts URL for a list of tournaments and optional dictionary of search parameters,
        fetches each page of results in turn, 
        fetches the html tags of each page using BeautifulSoup, 
        calls appropriate parsers to retrieve tagged data and then returns 
        a dataframe of tournamant data. Returns None if no results are found.
        Can search by tournament type and season passed via search_params
    '''

    def __init__(self,target,search_params,tourn_type):        
        self.target = target    # target URL
        self.params = search_params  # website search parameters
        if search_params.get('filter_by_event_type',False): 
            self.tourn_code = self.params['filter_by_event_type']
        else: self.tourn_code = 0  # assigned to National Events
        self.page_number = count(1)    # generator for page number
        self.results = pd.DataFrame()  # table to hold results
        self.tourn_type = tourn_type
        
    def page_of_soup_(self):               # generator of tagged results
        page_num = next(self.page_number)  # get next page number
        self.params['page'] = str(page_num) # update search terms to get next page
        html_ = requests.get(self.target , # retrieve next page of results
                             params = self.params  
                            )
        soup = BeautifulSoup(html_.text,'lxml')
        yield (soup)

    @property
    def tournament_list(self):  
        '''returns df of all tourns meeting search criteria 
            in self.search_params'''
        page_has_results = True
        while page_has_results:
            s = next(self.page_of_soup_())
            page_has_results = ( # Did site return "No results found"
                s.select_one(
                    TournamentLocators.USFA_LIST_FOUND).text.strip() != 'No results found.'
                                )
            if page_has_results:
                self.results = pd.concat(
                    [self.results, pd.DataFrame(  # parse data  from each tag into a single row
                        TournamentSummaryParser(tag_).all 
                            for tag_ in s.select(TournamentLocators.USFA_LIST)
                                              ).assign(type=self.tourn_type)  #add tournament type to the row
                    ]
                                        )

            page_wait = random.uniform(0,3)
            
            time.sleep(page_wait)
        print(f'retrieved {self.results.shape[0]} {self.tourn_type} tournaments') 
        # rename National tournament type to NAC
        self.results.loc[self.results['type'] == 'National','type'] = 'NAC'

        return self.results

class ScrapeTournamentDetails:
    '''
    accepts a USFA tournament id for a tournament and retrieves registration
    deadline dates from the USFA page for that tournament
    '''
    def __init__(self,tourn_id):        
        self.target = USFA_URLs.TOURNAMENT_DETAILS + str(tourn_id)   # target URL
        self.tourn_id = tourn_id
        
        self.html_ = requests.get(self.target ) # retrieve events
        self.soup = BeautifulSoup(self.html_.text,'lxml')
        
    @property
    def registration_dates(self):
        '''
        returns a tuple containing the Registration Open Date, the
        Registration Close Date and the Withdrawal Date
        '''
        return TournamentDetailParser(self.soup).registration_dates