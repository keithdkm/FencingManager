from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from fencingapp.models import User,Member


class LoginForm(FlaskForm):
    '''
    Form form user login
    '''
    username = StringField('Username',validators = [DataRequired()])  #<- arguments are the labesl to be used in the form
    password = PasswordField('Password',validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')   # <- in the case of a button, the argument 
                                        # is the label to be used in the button

class RegistrationForm(FlaskForm):
    '''
    Form to gather data to register a new user
    '''
    username = StringField('Username',validators = [DataRequired()])
    email = StringField('email address', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField('Re-enter Password',validators = [DataRequired(), EqualTo('password')])
    fencerid = StringField('USFA Membership #', validators = [Length(min=0,max=9)] )
    submit = SubmitField('Register')

    def validate_username(self,username):   #<- Flask WTF special method called "validate_%fieldname% "
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User name already taken. Please try a different name')
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already in use. Please use a different email')
    
    def validate_fencerid(self,fencerid):
        if fencerid.data:
            fencer = Member.query.get(int(fencerid.data))
            if not fencer:
                raise ValidationError('not a valid USFA Membership #. Please check your records')
