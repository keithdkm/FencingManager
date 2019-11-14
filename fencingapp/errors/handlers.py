from flask import render_template
from fencingapp import  db   # app instance is no longer required as decorators are
                            # provided from blueprint
from fencingapp.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.jinja2'),404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.jinja2'),500