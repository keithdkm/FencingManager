class TournamentLocators:
    '''
    CSS Selector to locate all tournaments on USFA tournament search result page
    '''
    USFA_LIST = 'div#search-contents table tbody tr'
    USFA_LIST_FOUND = 'div#search-contents'
    USFA_DETAILS = 'div.card'
    
    # locates all possible events scopes
    #USFA_EVENT_SCOPE_LOCATOR = 'select[name="event_scopes"]'  # finds the list of possible event scopes

class TournamentSummaryLocator:
    '''
    CSS selectors to pick out tournament summary data from USFA search results
    '''
    NAME = 'td div a'
    DATES = 'td '
    LOCATION = 'td'
    CODE = 'a[href]'   
    REG_DATES = 'div.card-body div.deadline'



