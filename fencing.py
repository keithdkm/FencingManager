'''
App to retrieve and analyse past and future fencing tournament results from the USA fenacing
and fencingtimelisve websites
'''


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
