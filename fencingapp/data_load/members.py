import logging
import pandas as pd
from pathlib import Path
from datetime import datetime as dt
import os

from fencingapp.models import Member 
from fencingapp import db
from fencingapp.data_load.URLs.URLs import USFA_URLs
from fencingapp.data_load.scrapers.members import memberFile

def load_members_to_db_from_csv():
    '''
    retrieves the files containing previous years' members,
    and concatentates with newly downloaded membership file 
    clears the existing contents of the members table
    fast load them into the members table using the SQLAlchemy Core for speed.
    '''
    logger = logging.getLogger('fencing')
    parse_date_cols = ["Expiration", 
                    #    "Birthdate"
                    #  "Background Check Expires",
                    #  "SafeSport Expires"
                      ]
    Member_table_empty = Member.query.count()==0
    # Fetch a fresh URL link for the current member list file
    THIS_SEASONS_MEMBERS = memberFile(USFA_URLs.USFA_MEMBER_LIST).url_link
    member_file_list=[THIS_SEASONS_MEMBERS]
    if Member_table_empty:  # if the member list is empty then reload ALL past member lists
        # TODO add logic to iterate through all the member files in this directory  
        basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'data')
        MEMBERS1819 = Path(basedir,'members1819.csv')  
        member_file_list.append(MEMBERS1819)

    # Load data from csv files and concatenate it together
       # files containing the member data 
    member_data = pd.DataFrame()   # Empty dataframe 
    for member_file in member_file_list: #concatenate this year's and last year's membership list
        member_data = member_data.append(
                        pd.read_csv(member_file, # this season's members
                                header = 0 ,
                                date_parser=pd.to_datetime, # which date parser to use
                                parse_dates = parse_date_cols, #which columns to parse as date
                                dtype = {'Suffix':str,'Club 1 ID#':str,'Club 2 ID#':str},
                                    ) 
                                        )
    # Remove duplicates, i.e. members who have re-upped and appear in both lists
    # Clean up missing values, set column types and drop unneeded columns
    member_data=(member_data.drop_duplicates('Member #','first')
                            .assign(Region = lambda df: df['Region #'].fillna(7).astype(int),       # International/Unassigned fencers get Region 7
                                    Birthdate = lambda df: df['Birthdate'].fillna(0).astype(int))  # for missing birthdates
                            .drop([ # drop unwanted columns
                               'Birthdate verified','Section','School Name','School Abbreviation',
                               'School ID#','CheckEd','US Citizen','Permanent Resident','Region #',
                               'Background Check Expires', 'SafeSport Expires'
                               ],axis =1) 
                            
                )
    # rename column names to match Member table
    member_data.columns = Member.__table__.columns.keys()[:23]
    
    # Populate date/time into updated and created fields
    member_data['updated_on'] = member_data['created_on'] = dt.utcnow()

    #clear the existing contents of the member table
    db.engine.execute('ALTER TABLE users DROP CONSTRAINT users_member_id_fkey')  # drop FK constraint with user table
    db.session.commit()
    Member.query.delete()
    db.session.commit()
    # add back FK constraint
    db.engine.execute('ALTER TABLE users ADD CONSTRAINT users_member_id_fkey FOREIGN KEY(member_id) REFERENCES members (id_)')
    db.session.commit()

    try:
        member_data.to_sql('members',db.engine,if_exists='append',index=False)
    except Exception as e:
        print ('Member list update failed. Error is', e)
    else:
        print('Member list updated successfully')

    return
    # Insert the dataframe into the database in bulk inserts of chunks of rows
    # db.session.execute(Member.__table__.delete())          # delete all rows from the members table
 
    ##################################################################
    # Using sqlalchemy core.  Not optimized for speed as this load is done infrequently
    # https://exceptionshub.com/bulk-insert-with-sqlalchemy-orm.html was a helpful source
    # could likely be done much faster with pandas_to_sql
    # chunk_size = 35   # take 35 rows at a time.  
    # member_data = member_data.to_dict(orient='split')['data']  # convert dataframe to list of lists
    # for rows in range(chunk_size,len(member_data), chunk_size):  # load 35 rows at a time , the max allowed by SQLite
    #     try:                                                     #  (24cols x 35 rows = 880, <999)
    #         db.session.execute(Member.__table__.insert().values(member_data[(rows-chunk_size):rows]))  # values here expects lists/tuples, without it
    #     except Exception as e:                                                          # a list of dicts must be passed
    #         logger.warning (f'{e.args}: Member data record chunk load failed for {member_data[(rows-chunk_size):rows]}' )
    #     else:
    #         logger.info(f'{Member.__tablename__} loaded successfully')



    #######################################################################
    # Produces pivot table or ratings broken down by region
    # df['rating'] = df['foil'].apply(lambda x:x[0])
    # df.pivot_table(values = ['id_'],
    #                 index = ['region'],
    #                 columns = ['rating'],
    #                 aggfunc=pd.Series.nunique,
    #                 fill_value=0).astype(int,errors='ignore')

    # Ratings by birthyear
    #df.pivot_table(values = ['id_'],index = ['birthdate'],columns= ['rating'],aggfunc=pd.Series.nunique,fill_value=0).astype(int,errors='ignore').loc[1995:2010,]
    #
    # Column totals for above pivot table