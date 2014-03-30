from sofly import db
from sofly.modules.users import constants as USER
import datetime

class User(db.Document):

    created = db.DateTimeField(default=datetime.datetime.now, required=True)
    first_name = db.StringField(max_length=20)
    last_name = db.StringField(max_length=30)
    email = db.EmailField(max_length=120, unique=True)
    password = db.StringField(max_length=120)
    role = db.IntField(default=USER.USER)
    status = db.IntField(default=USER.NEW)
    verified = db.BooleanField(default=False)

    def __unicode__(self):
        return self.email

    def get_status(self):
        return USER.STATUS[self.status]

    def get_role(self):
        return USER.ROLE[self.role]        

    meta = {
            'allow_inheritance': True,
            'indexes':  ['-created'],
            'ordering': ['-created']
        }        