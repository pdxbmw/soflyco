import www
from www import mail
from www.modules.results.models import Watch
from www.modules.users.models import User

import datetime

class CrawlerUtils(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def check_price_by_user(self, doc, search):
        itinerary = search.itineraries[0]
        for watcher in doc.watchers:
            paid = watcher.claims[-1].price if watcher.claims else watcher.reservation.get('paid')
            print 'User paid %s. Price is now %s.' % (paid, itinerary.price)
            if round(float(paid)) > round(float(itinerary.price)):
                mail.send_fare_alert(watcher, search)

    def crawl(self):
        print 'crawl init'
        with self.app.app_context():
            docs = Watch.objects(expires__gt=datetime.datetime.utcnow())
            print 'found %i docs' % len(docs)
            try:
                for doc in docs:
                    self.fetch(doc)
            except Exception as e:
                print e

    def fetch(self, doc):
        """

            Returns an instance of a Search object

        """
        if doc.search_params:
            search = www.utils.alaska.AlaskaUtils().crawl(doc.search_params)
            if search:
                identifier = doc.identifier
                search.set_itinerary_by_identifier(identifier)
                itinerary = search.itineraries[0]
                self.check_price_by_user(doc, search)
                doc.update_price(itinerary.price)            
        else:
            print "No search params in document."
        return