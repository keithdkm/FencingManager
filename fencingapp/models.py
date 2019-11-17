#  Fencing Competition Tracking and Planning
#  Author : Keith Miller
#  September 2019
#  Metadata for fencing database
'''
Fencing database metadata
'''
from datetime import datetime as dt
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from fencingapp import db, login # defined in __init__.py for fencingapp

# BUGS
# 1. [X] due to limit of number of host parameters in an insert (999), only 30 or so rows
#  with 32 columns can be passed to  the database. could b esped up by 
#  dropping unused columns thus allowing more rows to be sent at once OR 
#  using pandas df.to_sql()
# 2. [ ] pandas doesn't allow nulls in integer columns so club id columns are strings instead of 
#        integers. Should change to put zeroes the NA cols and revert type to integer

############################3
#  alembic does not detect all database changes
#  check https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect
#  for the list of things it can't do

# establish Base class to contain Table and Column definition classes
Base = db.Model

# Declare a classes to be mapped onto each db table

class Member(Base):     
    '''USFA members list keyed on member ID
    Contains expired members for competition history starting with the 18-19 Season
    '''
    __tablename__ = 'members'

    last_name = db.Column(db.String(80),nullable=True)
    first_name = db.Column(db.String(80,), nullable=True)                 
    middle_name  = db.Column(db.String(80,), nullable=True)   
    suffix  = db.Column(db.String(80,), nullable=True)    
    nickname  = db.Column(db.String(80,), nullable=True)  
    gender  = db.Column(db.String(80,), nullable=True)    
    birthdate  = db.Column(db.Integer, nullable=True) 
    # birthdate_verified = db.Column(db.String(80,), nullable=True)       
    division  = db.Column(db.String(80,), nullable=True)  
    # section  = db.Column(db.String(80,), nullable=True)   
    club_1_name = db.Column(db.String(80,), nullable=True)             
    club_1_abbreviation = db.Column(db.String(80,), nullable=True)       
    club_1_id  = db.Column(db.String(80,), nullable=True) 
    club_2_name = db.Column(db.String(80,), nullable=True)               
    club_2_abbreviation = db.Column(db.String(80,), nullable=True)       
    club_2_id  = db.Column(db.String(80,), nullable=True) 
    # school_name =  db.Column(db.String(80,), nullable=True)              
    # school_abbreviation =  db.Column(db.String(80,), nullable=True)      
    # school_id = db.Column(db.String(80,), nullable=True) 
    id_ = db.Column(db.Integer,primary_key = True, autoincrement = False)           # USFA Assigned member ID
    member_type  = db.Column(db.String(80,), nullable=True)       
    # checked  = db.Column(db.String(80,), nullable=True)       
    competitive  = db.Column(db.String(80,), nullable=True)       
    expiration  = db.Column(db.Date, nullable=True)        
    saber  = db.Column(db.String(5,), nullable=True)         
    epee  = db.Column(db.String(5,), nullable=True)      
    foil  = db.Column(db.String(5,), nullable=True)      
    # us_citizen  = db.Column(db.String(80,), nullable=True)        
    # permanent_resident  = db.Column(db.String(80,), nullable=True)        
    representing_country  = db.Column(db.String(80,), nullable=True)      
    region  = db.Column(db.Integer, nullable=True)        
    # background_check_expires  = db.Column(db.Date, nullable=True)       
    # safesport_expires = db.Column(db.Date, nullable=True)  
    created_on = db.Column(db.DateTime, default=dt.now)
    updated_on = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)    
    user = db.relationship('User',backref = 'member')
    

    def __repr__(self):
        return f'USFA Member {self.last_name}, {self.first_name} - {self.club_1_name}, {self.region} {self.id_}'
    
class Tournament(Base):
    __tablename__ = 'tournaments'
    
    id_ = db.Column(db.Integer,primary_key = True,autoincrement = False)    # USFA ID
    ft_id = db.Column(db.String(80))                  # Fencing Time Live ID
    venue = db.Column(db.String(80))
    city =  db.Column(db.String(80))
    state = db.Column(db.String(5))
    name = db.Column(db.String(80))  #tournament name
    opens = db.Column(db.DateTime)   # tournament registration opens
    closes = db.Column(db.DateTime)   # registration deadline
    withdraw = db.Column(db.DateTime) # withdrawal deadline
    start = db.Column(db.DateTime)   #tournament start date
    end = db.Column(db.DateTime)    # tournament end date
    region = db.Column(db.String(5)) 
    type = db.Column(db.String(20))
    season_id = db.Column(db.Integer,db.ForeignKey ('seasons.id_'))   # Creates the link to the season instance
    status = db.Column(db.String(15))  # <-this changed
    created_on = db.Column(db.DateTime, default=dt.now)
    updated_on = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)
    events = db.relationship('Event',
                                order_by = 'Event.start', 
                                backref = 'tournament',
                                lazy='dynamic',
                                cascade = "all,delete, delete-orphan")
    
    
    def __repr__(self):
        return f'{self.name}, {self.city}, {self.state}, {dt.strftime(self.start, "%B %d, %Y")}'

class Season(Base):
    '''
    Seasons run August 1st to July 31st and comprise a number of international, national 
    and regional tournaments
    '''
    # Add an init here to preprocess data strings into dates
    
    def __init__(self,s_date,e_date):
        super().__init__()
        self.start = s_date
        self.end = e_date

    # @property
    # def start(self):
    #     return self.__start
    # @start.setter
    # def start(self,value):
    #     self.__start = dt.strptime(value,"%d/%m/%y")
    #     print(f'Set start as {self.__start}')


    # @property
    # def get_end(self):
    #     return self.__end
    # @end.setter
    # def set_end(self,e_date):
    #     self.__end = dt.strptime(e_date,"%d/%m/%y")
    #     print(f'Set end as {self.__end}')



    __tablename__ = 'seasons'
    
    id_ = db.Column(db.Integer, primary_key = True,autoincrement = True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime, default=dt.now)
    updated_on = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)
    
    tournaments = db.relationship('Tournament', order_by = Tournament.start, backref = 'season') 
                                     # This defines 1: an attribute 'tournaments' on the Season object 
                                    #   that will list all the tournaments for that season AS OBJECTS
                                    #    AND
                                    # and create an attribute 'season' on each Tournament object that returns the Season object 
                                    # for that tournament.
    
    def __repr__(self):
        return (f"{dt.strftime(self.start,'%Y')}-{dt.strftime(self.end,'%y')} Season")

class Event(Base):
    '''
    A fencing competition comprised of a number of entrants, individual or team. 
    Each tournament is made up of one or more events
    '''
    __tablename__ = 'events'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(40), nullable=False)
    type = db.Column(db.String(10),nullable=False)
    weapon = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    abbreviation = db.Column(db.String(3),nullable=True)
    count = db.Column(db.Integer,nullable=True)   # entrant count
    rating = db.Column(db.String(2),nullable=True)  # calculated rating of event 
    tournament_id = db.Column(db.Integer,db.ForeignKey('tournaments.id_'))
    start = db.Column(db.DateTime)
    status = db.Column(db.String(10), nullable = True)
    created_on = db.Column(db.DateTime, default=dt.now)
    updated_on = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)

    def __repr__(self):
        return f'{self.name}, {self.rating} event with {self.count} entrants'
    
class Entrant(Base):
    __tablename__ = 'entrants'
    '''
    table containing the list of entrants for each event 
    It manages the many to many relationship between members and events downloaded
    from USFA fencing AND results downloaded from fencingtimelive
    '''
    # Design is based upon Chapter 56 of Flask mega tutorial. 
    # it will require a 
    # Changes required:
    # 1. [ ] Remove "id_" column. The member_id/event_id combo is unique
    # 2. [ ] Add an "entrants" relationship to the Event table
    # 3. [ ] Remove the "event" relationship in this table
    # 4. [ ] Add a "bouts" relationship to this table below
    # 5. [ ] Future - support for teams
    id_ = db.Column(db.Integer, primary_key = True, autoincrement = False)  # <== does this need to be here. Member/Event is unique
    member_id = db.Column(db.Integer, db.ForeignKey('members.id_'))  # entrant can be a team so could be 1 to many
    event_id = db.Column(db.Integer, db.ForeignKey('events.id_'))
    ### Build out code for many to many relatioship 
    ### between event and member here
    ### and connects back to itself via the bout table
    initial_seeding = db.Column(db.Integer)
    seeding_after_pools = db.Column(db.Integer)
    final_placing = db.Column(db.Integer)
    rating_earned = db.Column(db.String(5))
    created_on = db.Column(db.DateTime, default=dt.now)
    updated_on = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)
    event = db.relationship('Event',backref = 'entrants')  

class Bout(Base):
    __tablename__='bouts'
    '''
    This table is contains the results of completed bouts downloaded 
    from fencingtimelive
    '''
    # Changes required based upon Ch 56 of FMT.
    # this table connects two entrants to one another
    # similar to the Followers.Followed realtionship 
    id_ = db.Column(db.Integer, primary_key = True, autoincrement = False) 
    red_member_id = db.Column(db.Integer, db.ForeignKey('members.id_'))  
    green_member_id = db.Column(db.Integer,db.ForeignKey('members.id_'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id_'))
    pool_id = db.Column(db.Integer)
    round = db.Column(db.Integer)
    red_score = db.Column(db.Integer)
    green_score = db.Column(db.Integer)
    referee = db.Column(db.String(40))
    winner = db.Column(db.Integer,db.ForeignKey('members.id_'))

class User(UserMixin,Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    member_id = db.Column(db.Integer,db.ForeignKey('members.id_'))

    def __repr__(self):
        return '<User {}'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))   













