from flask import Blueprint, flash, g, jsonify, make_response, \
    redirect, render_template, request, session, url_for

from itsdangerous import BadSignature

from www import mail, security
from www.decorators import *
from www.modules.results.models import Price, Watch, Watcher
from www.utils.alaska import AlaskaUtils

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
    if request.method == 'POST':
        session['reservation'] = {
            'name': request.form['name'],
            'code': request.form['code']
            }
        print session['reservation']
    reservation = alaskaUtils.reservation(request)
    results = alaskaUtils.search(request, reservation=reservation)
    response = make_response(render_template('results/results.html', results=results))
    # kill session variable if request is successful
    #if session.has_key('reservation'):
        #session.pop('reservation')
    return response 

@module.route('/unwatch/<payload>', methods=['GET'])
def unwatch_from_email(payload):
    from www.helpers import redirect_url
    s = security.get_serializer()
    try:
        (identifier, email) = s.loads(payload)
        print (identifier, email)
    except BadSignature:
        abort(404)
    Watch.objects(identifier=identifier, watchers__email=email).update_one(set__watchers__S__watching=False)
    flash("You have been unsubscribed from any future price alerts on that flight.", 'warning')
    return redirect(redirect_url())

@module.route('/unwatch', methods=['POST'])
@login_required
@verified_required
def unwatch():
    response = 'failed'
    if g.user:
        # setup document
        identifier = request.form.get('id')
        # create or update document
        doc = Watch.objects(identifier=identifier, watchers__email=g.user.email).update_one(set__watchers__S__watching=False)
        response = 'success' if doc else 'error'
        # email user    
        email = g.user.email
        itinerary = alaskaUtils.itinerary_from_identifier(identifier)
        body = mail.watching_template(request, itinerary, email)
        #mail.send_email(g.user.email, 'Fare Alert Removed', body)   
    return jsonify(status=response)  

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
            watching = True,
            reservation = dict(
                code = request.form.get('code'),
                name = request.form.get('name'),
                paid = request.form.get('paid')
                ),
            #claims = [price] if request.form.get('claim') else []
            )
        #watch.update_one(add_to_set__watchers__S__claims=Price(price=price))
        # create or update document
        watch = Watch.objects(identifier=identifier).first()
        if watch:
            #Watch.objects(identifier=identifier).filter(watchers__email=email).update_one(add_to_set__watchers__S__claims=Price(price=price))
            # inefficient way to check if user previously unwatched
            # really shouldn't do it this way
            rewatch = Watch.objects(identifier=identifier, watchers__email=g.user.email).update_one(set__watchers__S__watching=True)
            if not rewatch:
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
        print(request.form)
        if request.form.get('claim') == 'true':
            Watch.objects(identifier=identifier).filter(watchers__email=g.user.email).update_one(add_to_set__watchers__S__claims=price)
        # email user    
        email = g.user.email
        itinerary = alaskaUtils.itinerary_from_identifier(request.form['id'])
        body = mail.watching_template(request, itinerary, g.user.email)
        mail.send_email(g.user.email, 'Fare Alert Added', body)   
        response = 'success'
    return jsonify(status=response)    