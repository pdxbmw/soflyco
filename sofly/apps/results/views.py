from flask import Blueprint, flash, g, jsonify, make_response, redirect, render_template, request, session, url_for

from sofly import log, mail, security
from sofly.apps.common.decorators import *
from sofly.apps.results.models import Price, Watch, Watcher
from sofly.utils.alaska import AlaskaUtils

import datetime

module = Blueprint('results', __name__, url_prefix='/results')

alaskaUtils = AlaskaUtils()

@module.route('/claim/<payload>')
def claim(payload):
    s = security.get_serializer()
    try:
        (identifier, email, price) = s.loads(payload)
        print (identifier, email, price)
    except BadSignature:
        abort(404)
    Watch.objects(identifier=identifier).filter(watchers__email=email).update_one(add_to_set__watchers__S__claims=Price(price=price))
    return redirect('https://www.alaskaair.com/booking/ssl/garr/GuaranteedAirfare.aspx', code=302)

@module.route('/', methods=['GET', 'POST'])
def results():    
    if request.method == 'POST' and session.has_key('search'):
        session['search'] = request.form
    results = alaskaUtils.search(request)
    response = make_response(render_template('results/results.html', results=results))
    if session.has_key('search'):
        pass#session.pop('search')
    return response    

@module.route('/reservation', methods=['GET', 'POST'])
def reservation():    
    # save user inputs in case an error handler's invoked
    if request.method == 'POST' and session.has_key('reservation'):
        session['reservation']['name'] = request.form['name']
        session['reservation']['code'] = request.form['code']
    reservation = alaskaUtils.reservation(request)
    results = alaskaUtils.search(request, reservation=reservation)
    response = make_response(render_template('results/results.html', results=results))
    # kill session variable if request is successful
    if session.has_key('reservation'):
        session.pop('reservation')
    return response 

@module.route('/watch', methods=['POST'])
@login_required
@verified_required
def watch():
    response = 'failed'
    if g.user:
        # setup document
        identifier = request.form.get('id')
        search_params = security.json_decrypt(request.form.get('search'))
        price = Price(price=request.form.get('price'))
        watcher = Watcher(
            email = g.user.email,
            reservation = dict(
                code = request.form.get('code'),
                name = request.form.get('name'),
                paid = request.form.get('paid')
                )
            )
        # create or update document
        watch = Watch.objects(identifier=identifier).first()
        if watch:
            watch.update(add_to_set__prices=price, add_to_set__watchers=watcher)
        else:
            watch = Watch(
                expires = datetime.datetime.strptime(search_params.get('DepartureDate1'),'%m/%d/%Y'),
                identifier = request.form.get('id'),
                prices = [price],
                search_params = search_params,
                watchers = [watcher]
                )
            watch.save()
        # email user    
        email = g.user.email
        itinerary = alaskaUtils.itinerary_from_identifier(request.form['id'])
        body = mail.watching_template(request, itinerary)
        mail.send_email(g.user.email, 'Fare Alert Added', body)   
        response = 'success'
    return jsonify(status=response)    