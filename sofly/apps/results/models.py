from sofly import db
from sofly.apps.users.models import User

import datetime

class Price(db.EmbeddedDocument):
    created = db.DateTimeField(default=datetime.datetime.utcnow)
    price = db.DecimalField(precision=2)

class Watcher(db.EmbeddedDocument):
    email = db.EmailField()
    reservation = db.DictField()
    claims = db.ListField(db.EmbeddedDocumentField(Price))

class Watch(db.Document):
    created = db.DateTimeField(default=datetime.datetime.utcnow)
    expires = db.DateTimeField(required=True)
    identifier = db.StringField(primary_key=True, required=True)
    search_params = db.DictField()
    prices = db.ListField(db.EmbeddedDocumentField(Price))
    watchers = db.ListField(db.EmbeddedDocumentField(Watcher))

    def __unicode__(self):
        return self.identifier

    def add_claim(self, email, paid):
        return self.filter(watchers__email=email).update_one(add_to_set__watchers__S__claims=Price(price=paid))

    def update_price(self, price):
        if round(self.prices[-1].price,) != round(float(price)):
            new_price = Price(price=price)  
            self.update(add_to_set__prices=new_price)     

    meta = {
            'allow_inheritance': True,
            'indexes':  ['-created'],
            'ordering': ['-created']
        }