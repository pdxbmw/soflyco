from flask import abort, flash, session, url_for

from bson.objectid import ObjectId
from datetime import datetime
from pymongo import Connection

import calendar
import config
import os

class MongoUtils(object):
    """
    This whole thing needs to be revised.
    """

    def __init__(self, app=None, **kwargs):
        self.uri = self.uri()
        self.conn = Connection(self.uri)        

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.log = app.logger
        self.app = app    

    def activate_user(self, user_id):
        try:                
            self.log.debug('user_id is: '+user_id)
            _id = ObjectId(user_id)
            coll = self.collection('users')
            user = coll.find_one({'_id':_id})
            if user:
                self.log.debug('user found')
                if session:
                    session['user']['verified'] = True
                user['verified'] = True
                coll.update({'_id':_id}, user, upsert=True)   
                self.log.debug('user activated')
                return True
            else:
                self.log.debug('no user with that id')
        except Exception as e:
            self.log.error(e)     
        return False

    def collection(self, collection):
        return self.conn.flights_pdxbmw[collection]

    def get_current_price(self, doc):
        try:                
            adioso = AdiosoUtils()
            coll = self.collection('watching')
            flight_id = doc['identifier']
            qs = adioso.id_to_qs(flight_id)
            q  = adioso.qs_to_q(qs)
            flights = adioso.flights(q)
            for flight in flights:
                if flight['identifier'] == flight_id:
                    return int(flight['price'])
                    '''
                    if int(doc['prices'][-1].get('price')) != current_price:
                        doc['prices'].append({
                            'date'  : now,
                            'price' : current_price
                        })  
                        print 'Updating price'
                        coll.update({'identifier':doc['identifier']}, doc, upsert=True)
                    for user in doc['users']:
                        if int(user['paid']) > current_price:
                            # price has gone down
                            print "PRICE HAS GONE DOWN."
                            MailUtils().send_fare_alert(flight, user['email'])
                    '''
            return True
        except Exception as e:
            print e
        return False

    def get_watching(self):
        try:                
            coll = self.collection('watching')
            docs = coll.find()
            return docs
        except Exception as e:
            return e                   

    def remove_exipred(self, doc):
        '''

            This should be done automatically with 
            the MongoDB TTL setting.


        '''
        if int(doc['expires']) < now:
            print ('EXPIRED. SKIPPING.', doc['identifier'])
            return True
        return False

    def update_price(self, doc, price):
        response = 'failed' 
        try:                
            coll = self.collection('watching')
            if doc['prices'][-1].get('price') != price:                
                doc['prices'].append({
                    'date'  : datetime.utcnow(),
                    'price' : price
                })  
                coll.update({'identifier':doc['identifier']}, doc, upsert=True)        
            response = 'success'
        except Exception as e:
            self.log.error(e)     
        return response 

    def update_user_paid(self, identifier, email, price):
        response = 'failed' 
        try:                
            coll = self.collection('watching')
            coll.update({'identifier': identifier, 'users.email': email}, 
                {'$addToSet' : {'users.$.claim' : {
                                'date' : datetime.utcnow(),
                                'paid' : price 
                }}}, 
            multi=False, upsert=True)
            #coll.update({'_id':_id}, doc, upsert=True)        
            response = 'success'
        except Exception as e:
            self.log.error(e)     
        return response         

    def verify_user(self, user, **kwargs):
        if user:
            try:                
                coll = self.collection('users')
                email = user.email
                if email:
                    exists = coll.find_one({'email':email})
                    if exists:
                        if not exists.get('verified'):
                            flash("Your email address has not been verified. <a href=\"%s\"> \
                                Click here to resend the verification email</a>." % url_for('users.activation_email'), 
                                category="warning")
                            return False
                        else:
                            flash("Welcome back, %s. You were successfully logged in." % exists.get('first_name'), 
                                category='success')
                            return True
                    else:    
                        doc = dict(
                            added       = datetime.utcnow(),
                            email       = email,
                            first_name  = user.first_name,
                            id          = user.id,
                            last_name   = user.last_name,
                            name        = user.name,
                            provider    = kwargs.get('provider'),
                            verified    = False
                        )
                        coll.update({'email':email}, doc, upsert=True)   
                        return False
                else:
                    flash("We couldn't located an email address for your login.", 
                        category='danger')
                return False
            except Exception as e:
                self.log.error(e)     
        flash("There was a problem logging you in.", category='danger')        
        return False

    def unwatch(self, request):
        form = request.form
        self.log.debug(request.GET.get('id'))

    def watch(self, request):
        try:
            coll = self.collection('watching')
            form = request.form
            self.log.debug(form)
            search, email, flight_id, price = form['search'], session['user']['email'], form['id'], form['price']
            #now = calendar.timegm(datetime.utcnow().utctimetuple())
            #expires = calendar.timegm(datetime.strptime(request.form['expires'],'%Y-%m-%d').utctimetuple())
            now = datetime.utcnow()            
            query = security.json_decrypt(search)
            data = dict(
                created = now,
                expires = datetime.strptime(query.get('DepartureDate1'),'%m/%d/%Y'),
                identifier = flight_id,
                prices  = [dict(
                    date  = now,
                    price = price
                )],
                search_params = query,
                users   = [dict(
                    email = email,
                    reservation  = dict(
                        last_name = form.get('name'),
                        paid = form.get('paid'),
                        ticket_code = form.get('code')
                    )
                )]
            )
            self.log.debug(data)
            exists = coll.find_one({'identifier':flight_id})
            if exists:
                # email
                prices, users = exists['prices'], exists['users']
                for user in users:
                    if not email in user['email']:
                        users.append(data['users'][0])
                data['users'] = users
                # price                      
                if prices[-1].get('price') != price:
                    prices.append(data['prices'][0])
                data['prices'] = prices
            coll.update({'identifier':flight_id}, data, upsert=True)        
            return True
        except Exception as e:
            self.log.error(e) 
            abort(400)
        return False

    def uri(self, host='localhost', port=27017, db='sofly'):
        if config.IS_DEV:
            print 'using local mongo db'
            uri = "mongodb://%s:%d/%s" % (host, port, db)   
        else:    
            uri = os.environ.get('MONGOHQ_URL')
            if not uri: # TODO: detect if prod
                uri = "mongodb://%s:%s@%s:%d/%s" % (
                    config.MONGO['username'],
                    config.MONGO['password'],
                    config.MONGO['hostname'],
                    config.MONGO['port'],
                    config.MONGO['db']
                )        
                #print >> sys.stderr, uri
                return uri
        #else:
            #uri = "mongodb://localhost:27017"       
        return uri