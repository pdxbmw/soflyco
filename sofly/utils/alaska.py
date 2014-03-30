from flask import abort, current_app

from sofly.helpers import FlashMessage, InvalidUsage, load_json_file
from sofly.utils.cache import CacheUtils
from sofly.utils.security import SecurityUtils

from collections import namedtuple, OrderedDict
from copy import deepcopy
from pyquery import PyQuery as pq
import calendar
import datetime
import json
import math
import os 
import pytz
import re
import requests

cacheUtils = CacheUtils()
security = SecurityUtils()

Links = namedtuple('Links', 'get_discount_code, lookup_airport, lookup_reservation, search_by_price, search_by_schedule')

AIRPORTS = load_json_file('airports')

URLS = Links(
        'https://www.alaskaair.com/shared/tips/AboutDiscountCodes.aspx?view=0&referrer=summary&code=',
        'http://www.alaskaair.com/HomeWidget/GetCities?prefixText=',
        'https://www.alaskaair.com/booking/reservation-lookup',
        'https://www.alaskaair.com/Shopping/Flights/Price',
        'https://www.alaskaair.com/Shopping/Flights/Shop'
)

class Segment(object):
    """

        Segments are the primitive data type

    """
    def __init__(self, origin, destination, depart, arrive, number='', duration=None):
        self.origin = origin
        self.destination = destination
        self.depart = depart
        self.arrive = arrive
        self.number = number
        self.duration = duration

class Flight(Segment):
    """

        Flights are made up of one or more segments
    
    """
    def __init__(self, **kwargs):
        super(Flight, self).__init__(**kwargs)
        self.add_segment()

    def __getitem__(self, key):
        return self.key
    
    def __setitem__(self, key, item):
        self[key] = item

    def add_duration(self, segment):
        layover = (segment.depart - self.arrive).seconds / 60
        hours = int(self.duration[0:2]) + int(segment.duration[0:2])
        total = layover + hours * 60 + int(self.duration[2:4]) + int(segment.duration[2:4])
        return '{:02d}{:02d}'.format(total/60, total%60)          
        
    def calculate_duration(self):
        
        def localize(airport, datetime):
            airport = AIRPORTS[airport]
            tz = pytz.timezone(airport['timezone'])
            return tz.localize(datetime, is_dst=airport['dst']=='A')

        depart = localize(self.origin, self.depart)
        arrive = localize(self.destination, self.arrive)
        diff = arrive - depart
        total_seconds = int(diff.total_seconds())
        hours, remainder = divmod(total_seconds,60*60)
        minutes, seconds = divmod(remainder,60)        
        self.duration = '{:02d}{:02d}'.format(hours, minutes)

    def add_segment(self, segment=None):      
        if segment:
            #self.duration = self.add_duration(segment) if segment.duration else self.duration
            self.arrive = segment.arrive
            self.destination = segment.destination
            self.add_stop(segment.origin)
            self.numbers.append(segment.number)
            self.segments.append(segment)    
        else:
            self.segments = [self]        
            self.connections = []
            self.identifier = None        
            self.stops = 0
            self.numbers = [self.number]
        
        self.calculate_duration()
        self.build_identifier()            

    def add_stop(self, airport=None):
        if airport:
            self.connections.append(airport)
        self.stops += 1

    def build_identifier(self):
        self.identifier = '%s%s%s%s%s%s%s%s%s%s' % (
            self.origin,
            self.depart.strftime('%Y%m%d'),
            self.depart.strftime('%H%M'),
            self.destination,
            self.arrive.strftime('%Y%m%d'),
            self.arrive.strftime('%H%M'),
            self.duration,
            self.stops,
            ''.join(self.numbers),
            ''.join(self.connections)
        )

    @property
    def attrs(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items()) 

class Itinerary(object):
    """

        Itineraries are made up of one or more flights
    
    """
    def __init__(self, origin=None, destination=None):
        self.destination = destination
        self.flights = []
        self.index = 0
        self.is_final_segment = False
        self.origin = origin
        
    def __getitem__(self, key):
        return self.key
    
    def __setitem__(self, key, item):
        self[key] = item

    def add_flight(self, flight=None, **kwargs):

        new_flight = flight or Flight(**kwargs)

        # set flag to create a new itinerary
        self.is_final_segment = new_flight.destination == self.destination

        # check if the new flight is a connecting flight
        if self.flights and new_flight.origin != self.origin:
            flight = self.flights[-1]
            # make sure not another option with the same origin, or the return flight of a round trip
            if new_flight.origin != flight.origin and new_flight.destination != flight.origin:
                flight.add_segment(segment=new_flight)              
                return self.flights[-1]
                     
        self.flights.append(new_flight)     
        return self.flights[-1]

    def from_identifier(self, identifiers):
        current_app.logger.debug(identifiers)

        def get_connections(text):
            return re.findall("([A-Z]{3})", text)

        def get_numbers(text):
            return re.findall("([A-Z]{2}[0-9]{2,4})", text)  

        def get_datetime(text):
            return datetime.datetime.strptime(text,'%Y%m%d%H%M') 

        for item in identifiers.split('|'):

            flight = self.add_flight( 
                origin = item[0:3],
                destination = item[15:18],
                depart = get_datetime(item[3:15]),
                arrive = get_datetime(item[18:30]),
                duration = item[30:34]
            )          
            flight.numbers = get_numbers(item[35:])
            flight.stops = item[34:35]
            flight.connections = get_connections(item[35:])

    @property
    def identifier(self):
        return '|'.join([flight.identifier for flight in self.flights])

    @property
    def num_flights(self):
        return len(self.flights)

    @property
    def is_one_way(self):
        return len(self.flights) == 1

    @property
    def is_round_trip(self):
        return len(self.flights) > 1 and self.flights[0].origin == self.flights[-1].destination

    @property
    def is_multi_city(self):
        return len(self.flights) > 1 and self.flights[0].origin != self.flights[-1].destination

    @property
    def attrs(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items()) 

class Reservation(Itinerary):
    """

        Reservations contain a single itinerary
    
    """    
    def __init__(self, request=None):
        super(Reservation, self).__init__()
        self.current_price = 0
        self.discount = 0
        self.last_name = None
        self.paid = 0
        self.request = request
        self.search_params = {}
        self.submit_attempts = 0
        self.ticket_code = None

    #def __getitem__(self, key):
    #    return self.key

    #def __setitem__(self, key, item):
    #    self[key] = item

    def abort(self):
        raise FlashMessage("Hmm, we couldn't locate a reservation. Make sure your information is correct and try again.",\
            category='danger')        

    def build_itinerary(self):

        def get_airport(element, string):
            node = element.find('td').filter(lambda i: string in pq(this).text().lower()).text()
            return re.search("^.*\((.*)\).*$", node).group(1)[:3]

        def get_datetime(element, index):
            # Just using travel dates for year now
            travel_date = self.travel_dates[index]
            (year, month, day) = travel_date.split('-')
            date = element.find('.FlightTimeContainer').text().split()
            # Trying lookup by abbreviated date
            months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            month = months[date[3]]
            twelve_hour = '%s %s' % (date[0], date[1])
            twenty_four = datetime.datetime.strptime(twelve_hour, '%I:%M %p').strftime('%H:%M').split(':')
            return datetime.datetime(int(year), int(month), int(date[4]), int(twenty_four[0]), int(twenty_four[1]))

        def get_cabin():
            text = self.html('.flightstable > tr').eq((index * 3)-1).text().lower()   
            return 'first' if re.match("^.*first.\(.\).*$", text) else 'coach'

        def get_duration(text):
            match = re.search('duration:(.*) ours (.*) inutes', text)
            return '{hours:02d}{minutes:02d}'.format(hours=int(match.group(1)[:-1]), minutes=int(match.group(2)[:-1]))           

        def get_stops(text):
            # 
            # TODO: I BELIEVE ALL SEGMENTS SAY "NONSTOP" 
            #       BUT NEED EXAMPLES
            # 
            return 0 if re.match("^.*nonstop.(.).*$", text) else 0            

        segments = self.html.find('[id^="FlightDetailInfo_"]')

        for index, segment in enumerate(segments):
        
            index += 1

            text = self.html('#FlightDetailInfo_%s' % index).text().lower()
            table = self.html('#FlightDetailInfo_%s .Details' % index)
            first_row = table.find('tr').eq(1)
            second_row = table.find('tr').eq(2)
            airline_code = first_row.find('img').attr('src')[-7:-5]
            flight_number = first_row.find('td').eq(0).text().split()[1]

            flight = self.add_flight(
                number = airline_code + flight_number,
                origin = get_airport(first_row, 'depart'),
                destination = get_airport(second_row, 'arrive'),                
                depart = get_datetime(first_row, index - 1),
                arrive = get_datetime(second_row, index - 1)
            )

            flight.cabin = get_cabin()
            flight.stops = get_stops(text)

    def check_for_discount_code(self):
        try:
            discount_src = self.html('#DiscountCodeTermsFrame')
            element = self.html('#priceSummaryContent').text().lower()
            match = re.search('discount code: (.*)', element)
            if match:
                response = requests.get(URLS.get_discount_code + match.group(1))
                self.discount = float(response.content.split('$')[1].split()[0])
        except Exception as e:
            current_app.logger.error(e)

    def check_for_schedule_change(self):
        if 'Confirm Your Schedule Change' in self.html:
            raise FlashMessage("Your schedule has changed and needs to be confirmed before proceeding.<br> \
                <a href='%s' target='_blank'>Click here to confirm your schedule change on alaskaair.com</a>"\
                % URLS.lookup_reservation, category='warning')  
        else:
            return False                         

    def dispatcher(self):
        response = self.fetch()
        self.parse(response)

    def fetch(self):
        self.submit_attempts += 1
        
        if not self.request.form:
            self.abort()

        try:

            self.last_name = self.request.form['name']
            self.ticket_code = self.request.form['code']
            
            values = dict(
                TravelerLastName = self.last_name,
                CodeOrNumber = self.ticket_code,
                Continue = 'Continue'
            )

            self.cache_key = ''.join([v for k, v in values.items()])
            cached = cacheUtils.get(self.cache_key)
            
            if not cached:
                response = requests.post(URLS.lookup_reservation, data=values)
                content = response.content
                current_app.logger.debug("Caching Alaska reservation search.")
            else:
                content = cached
                current_app.logger.debug("Found Alaska reservation in cache.")
        
            cacheUtils.set(self.cache_key, content, timeout=3600)

            return content
            
        except Exception as e:            
            current_app.logger.error(e)
            self.abort()

    def parse(self, content):
        junk = re.compile(r'[\n\r\t]')        
        self.html = pq(junk.sub('', content))

        self.set_travel_dates()
        self.check_for_schedule_change()
        self.check_for_discount_code()
        self.build_itinerary()
        self.set_search_params()
        self.set_payment_method()

    def set_payment_method(self):
        text = self.html('#divFareAndTaxes > div:first > .amount').text().lower()
        if 'miles' in text:
            self.miles = text
        else:
            self.paid = text[1:]

    def set_search_params(self):
        #
        # TODO: NOT SURE WHAT FLIGHTYPE IS
        #
        self.search_params['flightType'] = '1'

        if not len(self.flights):
            self.abort()
            
        self.search_params['CabinType'] = self.flights[0].cabin        

        if self.is_one_way:
            self.search_params['IsOneWay'] = 'true'
        elif self.is_round_trip:
            self.search_params['IsRoundTrip'] = 'true'
            self.search_params['ReturnDate'] = self.flights[-1].depart.strftime('%m/%d/%Y')
        else:
            self.search_params['IsMultiCity'] = 'true'


        for index, flight in enumerate(self.flights):

            index += 1

            if index > 1 and not self.is_multi_city:
                break 
                
            self.search_params['DepartureCity%s' % index] = flight.origin
            self.search_params['DepartureDate%s' % index] = flight.depart.strftime('%m/%d/%Y')
            self.search_params['ArrivalCity%s' % index] = flight.destination

    def set_travel_dates(self):
        try:
            attribute = self.html('.head.hotel a').attr('onclick')
            if attribute:
                match = re.search('^.*DateRange=(.*?)&.*$', attribute).group(1)
            else:
                current_app.logger.debug("Couldn't find date range in hotel link. Trying car link.")
                attribute = self.html('.head.car a').attr('onclick')
                match = re.search('.*DateTimeRange=(.*?)&.*', attribute).group(1)
            self.travel_dates = [date[:10] for date in match.split('%2C')]
        except TypeError as e:
            current_app.logger.error(("Problem with request. Removing from cache and retrying.",e))
            cacheUtils.delete(self.cache_key)
            if self.submit_attempts > 3:
                self.abort()
            else:
                self.fetch() 

class Search(object):
    """

        Searches contain collections of itineraries
    
    """        
    def __init__(self, request=None):
        self.cabin = 'coach'
        self.destinations = []
        self.itineraries = []
        self.id_table = {}
        self.is_by_price = False
        self.origins = []
        self.request = request
        self.reservation = None

    def __getitem__(self, key):
        return self.key

    def __setitem__(self, key, item):
        self[key] = item

    def abort(self):
        raise FlashMessage("Hmm, we didn't seem to have enough information to complete the request.",\
            category='danger')   

    def add_itinerary(self, new_itinerary):
        # don't add a new itineray
        if self.is_by_price and new_itinerary.is_final_segment:
            return
        
        self.itineraries.append(new_itinerary)

    def build_airport_list(self):            
        for key, value in sorted(self.search_params.items()):
            if 'City' in key:
                match = re.search('.*\((.{3}).*\)', value)
                value = match.group(1) if match else value.upper()
            if 'DepartureCity' in key:
                self.origins.append(value)
            elif 'ArrivalCity' in key:
                self.destinations.append(value)
        if self.is_round_trip:
            self.origins.append(self.destinations[0])
            self.destinations.append(self.origins[0]) 

    def build_id_table(self, id_list):
        for identifiers in id_list:
            current_table = self.id_table
            maximum = len(identifiers) - 1
            for index, identifier in enumerate(identifiers):
                if identifier not in current_table:
                    if index != maximum:
                        current_table[identifier] = {}
                    else:
                        current_table['price'] = identifier
                        break
                current_table = current_table[identifier]  

        self.id_table = json.dumps(self.id_table)


    def build_itineraries(self, elements):

        def get_datetime(text):
            return datetime.datetime.strptime(text,'%m/%d/%Y %I:%M:%S %p')            

        def get_segments(element):
            # segment info from Seats link
            text = str(element.find('a[title="Seats"]').attr('onclick')).split('&segs=')[1]
            return text.split('|')[:-1]

        def set_duration(flight, element):
            selector = '.smallText.rightaligned.DetailsSmall' if self.is_by_price else 'li.SegmentDiv > span'
            text = element.find(selector).text().split()
            time = (2,4) if self.is_by_price else (0,2)
            flight.duration = '{hours:02d}{minutes:02d}'.format(hours=int(text[time[0]][:-1]), minutes=int(text[time[1]][:-1]))
            flight.build_identifier()

        def set_flight_price(flight, element):
            # this is for itineraries by price
            text = element.find('.PriceCell div').text()
            flight.price = re.search("^\$(.*)\xa0total$", text).group(1).replace(',','')                 

        def set_flight_prices(flight, element, index):
            flight.prices = dict(
                coach = dict(
                    lowest = element.find('.BestDealColumn .Price').text()[1:],
                    refundable = element.find('.FullFlexColumn .Price').text()[1:]
                ),
                first = dict(
                    lowest = element.find('.FirstClassDealColumn .Price').text()[1:],
                    refundable = element.find('.FirstClassColumn .Price').text()[1:]
                )
            )
            chosen = self.reservation.flights[index].cabin if self.reservation else self.cabin
            unchosen = 'first' if chosen == 'coach' else 'coach'
            flight.price = flight.prices[chosen]['lowest'] or flight.prices[chosen]['refundable']
            if not flight.price:
                flight.price = flight.prices[unchosen]['lowest'] or flight.prices[unchosen]['refundable']
                flight.price_unchosen = True

        def set_reservation_price(new_flight):
            if self.reservation:
                for flight in self.reservation.flights:
                    if flight.identifier == new_flight.identifier:
                        flight.current_price = float(new_flight.price)
                        self.reservation.current_price += flight.current_price                

        def build_itineraries_by_price(table):
            """

                This is the non-standard alaskaair.com search response, 
                which include segments from other airlines that are bundled 
                together and listed by total price.

            """
            current_app.logger.debug("Coudn't find the schedule table. Looking in price table.")

            rows = pq(table).find('.Option')

            for index in range(len(self.origins)):
                self.itineraries.append(Itinerary(destination=self.destinations[index], origin=self.origins[index]))

            id_list = []

            for row in rows:
                
                row = pq(row)
                first_column = row.find('.FlightCell')      
                segments = get_segments(first_column)

                self.index, identifiers = 0, []
                
                for segment in segments:
                    items = segment.split(',')

                    itinerary = self.itineraries[self.index]

                    flight = itinerary.add_flight( 
                        number = items[1] + items[3],
                        origin = items[4],
                        destination = items[6],
                        depart = get_datetime(items[5]),
                        arrive = get_datetime(items[7])
                    )  

                    if itinerary.is_final_segment:
                        #set_duration(flight, first_column)
                        set_flight_price(flight, row)
                        set_reservation_price(flight)   
                        #print flight.price
                        identifiers.append(flight.identifier)
                        flight.duplicate = any(flight.identifier == x[self.index] for x in id_list)
                        itinerary = self.add_itinerary(itinerary)  
                        self.index += 1

                identifiers.append(flight.price)
                id_list.append(identifiers)
                
            self.build_id_table(id_list)


        def build_itineraries_by_schedule(tables):    
            """

                This is the standard alaskaair.com search response,
                which allows users to select each segment of their itinerary
                by schedule (and price).

            """    
            for index, table in enumerate(tables):
                rows = pq(table).find('.Option')
                
                itinerary = Itinerary(destination=self.destinations[index], origin=self.origins[index])

                for row in rows:
                    row = pq(row)
                    first_column = row.find('.FlightCell')      
                    segments = get_segments(first_column)
                    
                    for segment in segments:
                        items = segment.split(',')
                        
                        flight = itinerary.add_flight( 
                            number = items[1] + items[3],
                            origin = items[4],
                            destination = items[6],
                            depart = get_datetime(items[5]),
                            arrive = get_datetime(items[7])
                        )  

                    #set_duration(flight, first_column)
                    set_flight_prices(flight, row, index)
                    set_reservation_price(flight)   

                self.add_itinerary(itinerary)    

        # determine how to parse the html response
        if self.is_by_price:
            build_itineraries_by_price(elements)
        else:
            build_itineraries_by_schedule(elements)                

    def crawler(self, search_params):
        response = self.fetch(search_params)
        self.parse(response)

    def dispatcher(self, reservation):
        self.reservation = reservation
        response = self.fetch()
        self.parse(response)

    def fetch(self, search_params=None):

        try:

            self.search_params = search_params or self.get_search_params()

            self.search_params_encoded = security.json_encrypt(self.search_params)
            self.cabin = self.search_params['CabinType'].lower()
            self.build_airport_list()

            current_app.logger.debug(self.search_params)

            self.cache_key = ''.join([value for key, value in self.search_params.items()])
            cached = cacheUtils.get(self.cache_key)

            if not cached:
                response = requests.post(URLS.search_by_schedule, data=self.search_params)
                content = response.content
                current_app.logger.debug("Caching Alaska search.")
            else:
                content = cached
                current_app.logger.debug("Found Alaska search in cache.")

            cacheUtils.set(self.cache_key, content, timeout=3600)                       

            return content

        except Exception as e:
            current_app.logger.error(e)
            self.abort()

    def get_flights_by_identifier(self, identifier):
        flights = []
        identifier = identifier.split('|')
        for index, itinerary in enumerate(self.itineraries):
            for flight in itinerary.flights:
                if flight.identifier in identifier[index]:
                    flights.append(flight)
        return flights

    def get_itinerary_by_identifier(self, identifier):
        new_itinerary, price = Itinerary(), 0
        identifier = identifier.split('|')
        for index, itinerary in enumerate(self.itineraries):
            for flight in itinerary.flights:
                if flight.identifier in identifier[index]:
                    new_itinerary.add_flight(flight=flight)
                    price += float(flight.price)
        new_itinerary.price = '%.2f' % price 
        return new_itinerary   

    def set_itinerary_by_identifier(self, identifier):
        self.itineraries = [self.get_itinerary_by_identifier(identifier)]

    def get_price_by_identifier(self, identifier):
        price = 0
        flights = self.get_flights_by_identifier(identifier)
        for flight in flights:
            price += float(flight.price)
        return '%.2f' % price        

    def get_search_params(self):
        try:
            params = self.reservation.search_params if self.reservation else self.request.form
            allowed_params = ['IsRoundTrip','IsOneWay','IsMultiCity','ReturnDate','CabinType','flightType']
            allowed_params.extend([param + str(index + 1) for index in range(4) for param in ['DepartureCity','DepartureDate','ArrivalCity']])
            print params
            return {key: params[key] for key in params if key in allowed_params}
        except Exception as e:
            current_app.logger.debug("No search params sent with request.")
            current_app.logger.error(e)
            self.abort()            

    def parse(self, content):

        def get_primary_table():
            elements = self.html.find('.MatrixTable')
            if not elements:
                self.is_by_price = True
                elements = self.html.find('#BundledTable')
            return elements 

        junk = re.compile(r'[\n\r\t]')        
        self.html = pq(junk.sub('', content))

        elements = get_primary_table()
        
        if not elements:
            self.abort()

        self.build_itineraries(elements)              

    @property
    def num_flights(self):
        return len(self.itineraries)

    @property
    def num_itineraries(self):
        return [itinerary.num_flights for itinerary in self.itineraries]
            
    @property
    def is_one_way(self):
        return self.search_params.get('IsOneWay') == 'true'

    @property
    def is_round_trip(self):
        return self.search_params.get('IsRoundTrip') == 'true'

    @property
    def is_multi_city(self):
        return self.search_params.get('IsMultiCity') == 'true'


class AlaskaUtils:
    """

        AlaskaAirlines.com utilities

    """
    def airport(self, airport_code):
        return AIRPORTS[airport_code]

    def airports(self, request):
        response = requests.get('%s%s' % (URLS.lookup_airport, request.args.get('q','')))
        return response.json()

    def crawl(self, search_params):
        search = Search()
        search.crawler(search_params)
        return search

    def itinerary_from_identifier(self, identifier):
        itinerary = Itinerary()
        itinerary.from_identifier(identifier)
        return itinerary

    def reservation(self, request):
        reservation = Reservation(request)
        reservation.dispatcher()
        return reservation      

    def search(self, request, reservation=None):
        search = Search(request)
        search.dispatcher(reservation)
        return search