import googlemaps
from sqlalchemy.sql import func,or_
from sqlalchemy.orm import Session
from flask import render_template,flash, redirect,url_for, request
from flask_login import login_required, current_user

from datetime import datetime as dt
from datetime import timedelta
from werkzeug.urls import url_parse

from fencingapp.models import Member,Tournament,Season, Event, User
from fencingapp import db   # import Flask app database object
from fencingapp.main import bp

############################
# Flask endpoints
############################
@bp.route('/')
@bp.route('/index')  # creates mapping between given URL and the function it decorates
@bp.route('/tournament')
def tournament():
    '''
    Displays upcoming tournaments, both regional(NorthEast) and national, and returns the numbers
    of competitors and the rating of the event ()
    '''

    def distance(origin,tournaments):
        '''
        Accepts list of tournament City,State location data and returns a dictionary of 
        distance and drivetime data with an entry for each destination
        '''
        # TODO this method should use tournament ID as the key to the dict it returns
        # instead of the string

        destinations = [(t.id_,t.city+t.state) for t in tournaments]
        API_KEY = 'AIzaSyAnTAn2mg2Y8MhSub8MPs5SdAc9CEeIbsg'  # TODO move to config file
        client = googlemaps.Client(API_KEY)
        res = {}
        
        for i in range (0,len(destinations),25):  # max number of destinations in distance request is 25
                                                  # so split destination list into batches of 25
            dists = client.distance_matrix(origin,[ d[1] for d in destinations[i:(i+25)]],units='imperial')
            
            if dists['status'] == 'OK':
                for n,d in enumerate(dists['destination_addresses']):
                    row_element = dists['rows'][0]['elements'][n]
                    if row_element['status'] == 'OK':
                        res[destinations[i+n][0]] = (row_element['distance']['text'],row_element['duration']['text'])
                    else:
                        res[destinations[i+n][0]] = 'Not Found','Not Found'    

        return res

    today = dt.utcnow()
    this_time_last_year = today - timedelta(days=365)
    
    this_season = Season.query.filter(
        Season.start<=today,Season.end>=today).first()
    last_season = Season.query.filter(
        Season.start<=this_time_last_year,Season.end>=this_time_last_year).first()
    

    TARGET_TOURNAMENTS = ['NAC','JO','ROC','SJCC',"National"]
    TARGET_EVENTS = ['Cadet', 'Junior', 'Division II', 'Division IA', 'Division I']
    TARGET_WEAPONS = ['Foil']
    TARGET_GENDERS = ['Women']
    YESTERDAY = dt.now() - timedelta(days=1)

    tourn_l =  (Tournament.query.filter(
                                    or_(Tournament.type.in_(TARGET_TOURNAMENTS),Tournament.region=='3'))
                                .filter((Tournament.end )>YESTERDAY)
                                .order_by(Tournament.start))

    if not tourn_l:
        return render_template('errors/404.jinja2',message = 'No Tournaments found')
    else:
        event_l = [(t,{a.type:a for a in t.events   #select only those events that are Women, Foil and 
            .filter(db.and_(Event.weapon.in_(TARGET_WEAPONS),   # in the right age groups and return in dictionary
                            Event.gender.in_(TARGET_GENDERS),  # should this logic be on the page
                            Event.type.in_(TARGET_EVENTS)))}) for t in tourn_l]

        # fetch dict of distances and drive times to event
        # TODO set start point to be start point of signed in user
        tournament_distances = distance(['Concord,MA'],tourn_l)

        refresh_date = Event.query.with_entities( 
                            func.max(Event.updated_on)).first()

        return render_template('main/tournament_list.jinja2',
                                tournaments = event_l, 
                                distances = tournament_distances,
                                refresh_date = refresh_date,
                                title = 'Tournaments')


@bp.route('/club')
@login_required    # only logged in users can see this view
def club():
    
    club_members = (db.session.query(Member.id_,Member.last_name, Member.first_name, Member.foil,Member.birthdate,Member.club_1_name)
                .filter(Member.club_1_name == Member.query.get(current_user.member_id).club_1_name)
                .filter(Member.foil != 'U')
                .filter(Member.gender == 'F')
                # .order_by(Member.foil)
                .all())

    club_members = sorted(club_members,key = lambda x:(x[3][0],-int(x[3][1:]),int(x[4])))   
            
    return render_template('main/member_list.jinja2', 
                            members=club_members, 
                            title='Female Foilists')


@bp.route('/USFA')
def USFA():
    '''
    Returns list of all female foilists
    '''
   
    USFA_members = (Member.query
            .filter(Member.foil != 'U')
            .filter(Member.gender == 'F')
            .all())

    USFA_members = sorted(data = USFA_members,
                          key = lambda member:(
                              member.region,
                              member.foil[0],
                              -int(member.foil[1:]),
                              member.last_name,
                              member.first_name))  

        # sort output by region, rating,rating year desc and then last name,first name
    return render_template('main/USFA_list.jinja2', members=USFA_members, title='USFA Rated Female Foilists')


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('main/member.jinja2',member=user.member)


@bp.route('/member/<member_id>')
@login_required
def member(member_id):
    member = Member.query.get(int(member_id))
    return render_template('main/member.jinja2',member=member)
