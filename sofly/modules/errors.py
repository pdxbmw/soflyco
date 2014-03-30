from flask import Blueprint, jsonify, flash, \
    make_response, redirect, render_template
    
from sofly.helpers import FlashMessage, InvalidUsage
    
module = Blueprint('errors', __name__)

@module.app_errorhandler(400)
def failed(e, **kwargs):
    log.error(e)
    return jsonify(status=kwargs.get('status','failed')), 400

@module.app_errorhandler(401)
def not_authorized(e):
    log.error(e)
    return jsonify(status='logged out'), 401

@module.app_errorhandler(403)
def not_verified(e):
    log.error(e)
    return jsonify(status='unverified'), 403

@module.app_errorhandler(404)
def not_found(e):
    log.error(e)
    return render_template('404.html')

@module.app_errorhandler(500)
def server_error(e):
    log.error(e)
    return render_template('500.html')    

@module.app_errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response  

@module.app_errorhandler(FlashMessage)
def app_errorhandler(error):
    #response = jsonify(error.to_dict())
    #response.status_code = error.status_code
    flash(message=error.message, category=error.category)
    response = make_response(redirect(redirect_url()))
    return response
