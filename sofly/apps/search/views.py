from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask import abort, jsonify, make_response

from sofly import db
from sofly.apps.search.forms import OneForm, MultiForm
from sofly.utils.alaska import AlaskaUtils

import json

module = Blueprint('search', __name__, url_prefix='/search')

alaskaUtils = AlaskaUtils()

@module.route('/')
def search():    
    if not session.has_key('search'):
        session['search'] = {}
    return render_template('search/search.html')

@module.route('/airport/<airport_code>')
def airport(airport_code):
    return json.dumps(alaskaUtils.airport(airport_code))

@module.route('/airports')
def airports():
    return json.dumps(alaskaUtils.airports(request))

@module.route('/reservation')
def reservation():
    if not session.get('reservation'):
        session['reservation'] = {'name':'','code':''}
    return render_template('search/search.html', reservation=True)         
