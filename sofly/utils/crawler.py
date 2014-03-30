from sofly import mail, security
from sofly.modules.results.models import Watch
from sofly.modules.users.models import User
from sofly.utils.alaska import AlaskaUtils

from pprint import pprint
import datetime

alaskaUtils = AlaskaUtils()

class CrawlerUtils(object):

    def check_price_by_user(self, doc, search):
        itinerary = search.itineraries[0]
        for watcher in doc.watchers:
            paid = watcher.claims[-1].get('paid') if watcher.claims else watcher.reservation.get('paid')
            if round(float(paid)) > round(float(itinerary.price)):
                print 'User paid %s. Price is now %s.' % (paid, itinerary.price)
                mail.send_fare_alert(watcher, search)

    def crawl(self):
        docs = Watch.objects(expires__gt=datetime.datetime.utcnow())
        for doc in docs:
            try:
                search = self.fetch(doc)
                if search:
                    identifier = doc.identifier
                    search.set_itinerary_by_identifier(identifier)
                    itinerary = search.itineraries[0]
                    self.check_price_by_user(doc, search)
                    doc.update_price(itinerary.price)
            except Exception as e:
                print e

    def fetch(self, doc):
        """

            Returns an instance of a Search object

        """
        if doc.search_params:
            return alaskaUtils.crawl(doc.search_params)
        else:
            print "No search params in document."
        return