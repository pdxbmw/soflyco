from flask import abort, g, jsonify, flash, make_response, redirect, render_template, request, session, url_for

from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter
from bson import ObjectId
from itsdangerous import BadSignature
from werkzeug.datastructures import ImmutableMultiDict

from sofly import app, log, mail, security
from sofly.apps.common.decorators import *
from sofly.apps.common import filters
from sofly.apps.common.helpers import *
from sofly.apps.users.views import User
from sofly.utils.alaska import AlaskaUtils
from sofly.utils.crawler import CrawlerUtils
from sofly.utils.cache import CacheUtils
from sofly.utils.mail import MailUtils
from sofly.utils.mongo import MongoUtils

import calendar, datetime, json
import config


""" TO DELETE """
""" TO DELETE """
""" TO DELETE """
# THESE ARE TEMP FOR EMAIL TEMPALTE BULDING
from jinja2 import Environment, FileSystemLoader
import os, premailer
""" TO DELETE """
""" TO DELETE """
""" TO DELETE """

#log = app.logger

# config 
authomatic = Authomatic(config=config.config, 
                        secret=config.SECRET_KEY, 
                        report_errors=True,
                        logging_level=log.level)

# glboals
alaskaUtils = AlaskaUtils()
crawlerUtils = CrawlerUtils()
mongoUtils = MongoUtils()


@app.before_request
def before_request():
    """
    Pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.objects.get(id=ObjectId(session['user_id']))

#########################
#
#        GENERAL
#
######################### 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select')
def select():
    return render_template('select.html')    

@app.route('/crawl')
def crawl():
    print request.args.get('token','')
    if request.args.get('token','') == 'mcHX47n8R3qe3z5bHuuWJGscWASapY2Aa9THDeSmraNh2vxskCSTy45qEvbuZkCZ':
        crawlerUtils.crawl()
    return redirect(redirect_url())

""" TO DELETE """
""" TO DELETE """
""" TO DELETE """
@app.route('/email/<template>')
def email(template):  

    search_params = {u'IsRoundTrip': u'true', u'ReturnDate': u'03/25/2014', u'DepartureCity1': u'pdx', u'ArrivalCity1': u'sea', u'DepartureDate1': u'03/25/2014', u'CabinType': u'coach'}
    identifier = 'PDX201403250845SEA20140325093300480AS2128|SEA201403251605PDX20140325165200470AS2061'
    search = alaskaUtils.crawl(search_params)
    search.set_itinerary_by_identifier(identifier)
    itinerary = search.itineraries[0]
    #itinerary.price = search.get_price_by_identifier(identifier)

    template_dir = os.path.join(app.root_path, app.template_folder)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['duration'] = filters.duration
    env.filters['no_stops'] = filters.no_stops    
    env.globals['url_for'] = url_for
    
    template = env.get_template('email/%s.html' % template)
    
    subject = 'Fare Alert: '
    for flight in itinerary.flights:
        subject += '%s >> %s, %s' % (
                flight.origin,
                flight.destination,
                flight.depart
            )
    #if flight.get('inbound'):
    #    subject += ', Returning %s' % flight['inbound']['departure_date']
    html = template.render(dict(
        search_params = None,
        reservation = dict(paid = '453.50'),
        itinerary = itinerary
    ))
    #return html
    out = premailer.Premailer(html, 
            include_star_selectors=True,
            exclude_pseudoclasses=True
        ).transform()    
    #mailUtils.send_email('pdxandi@gmail.com', subject, out)
    return out
""" TO DELETE """
""" TO DELETE """
""" TO DELETE """


#########################
#
#        ERRORS
#
#########################
@app.errorhandler(400)
def failed(e, **kwargs):
    log.error(e)
    return jsonify(status=kwargs.get('status','failed')), 400

@app.errorhandler(401)
def not_authorized(e):
    log.error(e)
    return jsonify(status='logged out'), 401

@app.errorhandler(403)
def not_verified(e):
    log.error(e)
    return jsonify(status='unverified'), 403

@app.errorhandler(404)
def not_found(e):
    log.error(e)
    return render_template('404.html')

@app.errorhandler(500)
def server_error(e):
    log.error(e)
    return render_template('500.html')    

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response  

@app.errorhandler(FlashMessage)
def errorhandler(error):
    #response = jsonify(error.to_dict())
    #response.status_code = error.status_code
    flash(message=error.message, category=error.category)
    response = make_response(redirect(redirect_url()))
    return response

#########################
#
#        HELPERS
#
#########################
def is_ajax(request):
    return 'XMLHttpRequest' in request.headers.get('X-Requested-With','')
