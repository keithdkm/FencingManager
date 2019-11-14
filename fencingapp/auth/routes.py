from flask import render_template, redirect,url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user,logout_user, current_user

from fencingapp.auth import bp
from fencingapp.auth.forms import LoginForm, RegistrationForm

from fencingapp.models import User
from fencingapp import db   # import db object


@bp.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:  # if user is logged in already
        return (url_for('main.tournament'))  # take them to tournaments page
    form = LoginForm()  # create an instance of form to retrieve login inro
    if form.validate_on_submit():  # if user submits valid input, search user table
        user = User.query.filter_by(username = form.username.data).first() 
        next_page = request.args.get('next')    # if user was trying visit a page that required login
                                               # return that page. 
        if not next_page or url_parse(next_page).netloc != "":  # ensure that URL wasn't hacked by checking for empty domain
                                                                # as all valid flask paths are relative
            next_page = url_for('auth.login')     # by default, return user to tournament page

        if not (user and user.check_password(form.password.data)): 
            flash('Invalid username or password') # does user exist and is pw correct
            return redirect(next_page)    # if not return to login page
        login_user(user,remember=form.remember_me.data) # if valid, log user in
        # next_page = request.args.get('next')    # if user was trying visit a page that required login
        #                                        # return that page. 

        return redirect(next_page)     # and send them to tournament page
    return render_template('auth/login.jinja2', title = 'Sign In',form = form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.tournament'))


@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # if user is logged in already
        return (url_for('main.tournament'))  # take them to tournaments page 
    form = RegistrationForm()
    if form.validate_on_submit():  # if form submission passes validation then create the user in db
        user = User(username=form.username.data, email=form.email.data,member_id=int(form.fencerid.data))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('auth.login')) # once registered, ask them to login
    return render_template('auth/register.jinja2',title='Register',form=form)

