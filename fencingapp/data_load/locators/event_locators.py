class EventLocators:
    '''
    CSS Selector to locate all events on USFA tournament page
    '''
    EVENT_LIST = 'div[data-event_id]' # locate div tags with a data-event_id attribute

class EventSummaryLocator:
    '''
    CSS Selectors to pick out event summary data from tournament page
    '''
    NAME = 'span.name'
    DATE = 'p'   # found on the first p tag of the parent
    TIME = ''
    ID = ''
    ABBREVIATION = ''
    SIZE = ''