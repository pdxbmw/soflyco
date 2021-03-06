from www import db
from www.modules.users.models import User

import datetime

class Price(db.EmbeddedDocument):
    created = db.DateTimeField(default=datetime.datetime.utcnow)
    price = db.DecimalField(precision=2)

class Watcher(db.EmbeddedDocument):
    email = db.EmailField(unique=True)
    watching = db.BooleanField()
    reservation = db.DictField()
    claims = db.ListField(db.EmbeddedDocumentField(Price))

class Watch(db.Document):
    created = db.DateTimeField(default=datetime.datetime.utcnow)
    updated = db.DateTimeField(default=datetime.datetime.utcnow)
    expires = db.DateTimeField(required=True)
    identifier = db.StringField(primary_key=True, required=True)
    search_params = db.DictField()
    prices = db.ListField(db.EmbeddedDocumentField(Price))
    watchers = db.ListField(db.EmbeddedDocumentField(Watcher))

    def __unicode__(self):
        return self.identifier

    '''
    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        return super(Watch, self).save(*args, **kwargs)
    '''

    ### THESE DON'T WORK
    def add_claim(self, email, paid):
        return self.filter(watchers__email=email).update_one(add_to_set__watchers__S__claims=Price(price=paid))

    def get_claims(self, email):
        return [watcher.claim for watcher in self.watchers if watcher.email == email]

    def unwatch(self, email):
        return self.filter(watchers__email=email).update_one(set__watchers__S__watching=False)

    def update_price(self, price):
        if round(self.prices[-1].price,) != round(float(price)):
            new_price = Price(price=price)  
            self.updated = datetime.datetime.now()
            self.update(add_to_set__prices=new_price)   
    ###

    meta = {
            'allow_inheritance': True,
            'indexes':  ['-created'],
            'ordering': ['-created']
        }