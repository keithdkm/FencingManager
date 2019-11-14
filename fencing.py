'''
App to retrieve and analyse past and future fencing tournament results from the USA fenacing
and fencingtimelisve websites
'''

# 1.[X] Code searches of event scope, but that doesn't find everthing.  need to seach on "Circuit"
# 2.[X] Searching on NAC doesn' bring up all the NACS.  Need to search using the National search
# 3.[X] should check when tournament table was last updated. If more than a week old,
#       rescrape data otherwise return contents of database
# 4.[X] Improve page fetch logic to DRY
# 5.[X] separate logic into function to process national and regional tournaments
# 6.[X] Database table refresh to be done with single update rather than a loop
# 7.[ ] one fewer records in table than reported by app. need to validate data
# 8.[X] use INSERT OR REPLACE for Tournament data update and remove 
# 9.[X] rewrite refresh logic for tournament and member data
#10.[X] create a virtual environment for the app to run in
#11.[X] install Flask-sqlAlchemy
#12.[X] restructure directories for Flask SQL Alchemy
#13.[X] rewrite models.py to use flask
#13.[ ] move project to github


# My modules
from fencingapp import create_app,db   # import Flask app instance and database
from fencingapp.models import Tournament,Event,User,Member,Season


app = create_app()
# app.app_context().push()  
# from fencingapp.data_load import refresh_data


@app.shell_context_processor
def make_shell_context():   # automatically adds database engine and model to flask session
    return {
            "db":db, 
            "Tournament": Tournament, 
            "Event": Event, 
            "User": User, 
            "Member": Member,
            "Season": Season
            }







############  END OF CODE   ##############
