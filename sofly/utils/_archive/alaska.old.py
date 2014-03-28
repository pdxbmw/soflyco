
class AlaskaUtils(object):
    """

        AlaskaAirlines.com utilities

    """

    def __init__(self):
        self.retries = 0
        
    def airports(self, request):
        response = requests.get('%s%s' % (URLS.lookup_airport, request.args.get('q','')))
        return response.json()

    def reservation(self, request):
        reservation = Reservation()
        reservation.get_reservation(request)
        log.debug(reservation)
        return reservation
            
    """            
    def reservation(self, request):

        # flight details
        def _reservation_data(i, _travel_date):
      
        
        #values = {'TravelerLastName':'Sherman','CodeOrNumber':'NRVCPP','Continue':'CONTINUE'}
        #values = {'TravelerLastName':'Greisel','CodeOrNumber':'EVXDQD','Continue':'CONTINUE'}
        try:
            data = request.form if request.method == 'POST' else request.args
            
            if not data:
                abort(400)

            values = dict(
                TravelerLastName = data['name'],
                CodeOrNumber     = data['code'],
                Continue         = 'CONTINUE'
            )
            key = ''.join([v for k, v in values.items()])
            
            c = cacheUtils.get(key)
            
            if not c:
                r = requests.post(self.RESERVATION_URL, data=values)
                log.debug(('making request: %s' % r.url, values))
                c = r.content
                log.debug("Caching Alaska reservation search.")
            else:
                log.debug("Found Alaska search in cache.")
        
            cacheUtils.set(key, c, timeout=3600)       
        except Exception as e:
            log.error(e)
        
        junk = re.compile(r'[\n\r\t]')        
        self.html = pq(junk.sub('',c))    

        # travel dates (oye)
        try:
            s = self.html('.head.hotel a').attr('onclick')
            a = re.search("^.*DateRange=(.*?)&.*$", s).group(1)
            travel_dates = a.split('%2C')        
        except TypeError as e:
            log.error(("Problem with request. Removing from cache and retrying.",e))
            cacheUtils.delete(key)
            if 'Confirm Your Schedule Change' in c:
                raise FlashMessage("Your schedule has changed and needs to be \
                    confirmed before proceeding. <br> \
                    <a href=\"%s\" target='_blank'>Click here to confirm your \
                    schedule change on alaskaair.com</a>" % self.RESERVATION_URL,
                    category='warning')
            self.retries += 1
            if self.retries > 2:
                raise FlashMessage("Hmm, we couldn't locate a reservation. Make sure \
                    your information is correct and try again.", category='danger')
            return self.reservation(request)

        # output
        out = []
        items = self.html.find('[id^="FlightDetailInfo_"]')
        num_items = len(items)
        for i in range(num_items):
            j = i + 1
            _travel_date = travel_dates[1] if j == num_items else travel_dates[0]
            out.append(_reservation_data(j, _travel_date))

        discount = 0
        try:
            discount_src = self.html('#DiscountCodeTermsFrame')
            _ps = self.html('#priceSummaryContent').text().lower()
            code = re.search('discount code: (.*)', _ps)
            if code:
                _r1 = requests.get(self.DISCOUNT_URL + code.group(1))
                discount = float(_r1.content.split('$')[1].split()[0])
        except Exception as e:
            log.debug("No discount code.")
            log.error(e)

        itinerary = {}

        # TODO: logic to detect multiple connection returning flights
        is_one_way = False
        if len(out) > 1:
            if out[0]['origin'] == out[-1]['destination']:
                itinerary['IsRoundTrip'] = 'true'
                itinerary['ReturnDate']  = out[-1]['segment'][0]['departure']['datetime'].strftime('%Y/%m/%d')
                #itinerary['ReturnTime']  = rtn['o_d_tm']
        else:
            is_one_way = True
            itinerary['IsOneWay'] = 'true'

        # some ugly stuff to account for connections
        last_date, i = [], 1
        for idx, item in enumerate(out):
            first = item['segment'][0]
            if is_one_way or item != out[-1]:
                date = first['departure']['datetime'].strftime('%Y/%m/%d')
                if last_date != date:
                    i = idx + 1
                    itinerary['DepartureCity%s'%i] = first['departure']['airport_code']
                    itinerary['DepartureDate%s'%i] = date
                    #itinerary['DepartureTime%s'%i] = dpt['o_d_tm']
                itinerary['ArrivalCity%s'%i] = first['arrival']['airport_code']
                last_date = date

        # TODO: Logic for multi-city
        itinerary['flightType']  =  '1'
        itinerary['IsMultiCity'] = 'false'
        itinerary['CabinType']   = out[0]['class']

        log.debug(out)
        log.debug(itinerary)

        paid, miles = self.html('#divFareAndTaxes > div:first > .amount').text().lower(), None
        if 'miles' in paid:
            miles = paid
        else:
            paid = paid[1:]

        return dict(
            code      = data['code'],
            discount  = discount,  
            itinerary = itinerary,
            miles     = miles,            
            name      = data['name'],
            paid      = paid,
            segment   = out            
        )   
    """         

    def _data_to_id(self, obj, airline=''):
        log.debug(obj)
        s = obj['duration'].split()
        duration = '%02d%02d'%(int(s[0][:-1]), int(s[1][:-1]))

        out = '%s%s%s%s%s%s%s%s%s%s' % (
            obj['segment'][0]['departure']['airport_code'],
            obj['segment'][0]['departure']['datetime'].strftime('%Y%m%d'),
            obj['segment'][0]['departure']['datetime'].strftime('%H%M'),
            obj['segment'][-1]['arrival']['airport_code'],
            obj['segment'][-1]['arrival']['datetime'].strftime('%Y%m%d'),
            obj['segment'][-1]['arrival']['datetime'].strftime('%H%M'),   
            duration,
            obj['no_stops'],
            ''.join(['%s%s'%(airline, i['flight_no']) for i in obj['segment']]),
            ''.join(obj['stops'])
        )
        log.debug(out)
        return out


    def _id_to_data(self, id):

        def _datetime(s):        
            return datetime(int(s[3:7]), int(s[7:9]), int(s[9:11]), int(s[11:13]), int(s[13:15]))
            
        out = []
        flights = id.split('|')
    
        stops = []
        for i in d:
            m = (re.match('[A-Z]{3}',i))
            if m:
               stops.append(m.group())
    
        # remove airports
        [d.remove(i) for i in stops if i in d]

        for flight in flights:
            d = re.sub( r'([A-Z]{1,3})', r' \1', flight).split()

            # standard format
            """


                NEEDS REVISING


            """

            # standard format
            obj = {'segment':[]}
            obj['segment'].append(dict(
                flight_no        = d[2:],
                departure = dict(
                    airport_code = d[0][:3],
                    datetime     = _datetime(d[0])
                ), 
                arrival = dict(
                    airport_code = d[1][:3],
                    datetime     = _datetime(d[1])
                ),          
            ))
            obj['duration'] = d[1][15:19],
            obj['no_stops'] = d[1][19:20],
            obj['stops']    = stops[2:]                    
            out.append(obj)    

        log.debug(out)

        return out      
            
    def _price_data(self, items, data):
        out, dups, list_ids, id_table = [], [], [], {}
        for item in items:
            el = pq(item)
            fc = el.find('.FlightCell')
            od = fc.find('.OptionDetails')
            price = el.find('.PriceCell div').text()
            dur = od.find('.smallText.rightaligned.DetailsSmall').text().split()
            params = dict(
                orig      = '',
                dest      = '', 
                no_stops  = '',
                duration  = '',
                flight_no = [],
                segment   = [],
                stops     = [],
                duplicate = False
            )
            segs = str(fc.find('a[title="Seats"]').attr('onclick')).split('&segs=')[1].split('|')[:-1]
            els = fc.children('acronym, img')
            num_els, num_segs, cnt = len(els), len(fc.find('img#to')), 0
            objs = [deepcopy(params) for k in range(num_segs)]
            cnt = 0
            for idx, val in enumerate(els):
                if val.tag == 'acronym':
                    airport = pq(val).text()
                    # last item is dest
                    if idx == num_els-1:
                        objs[cnt]['dest'] = airport
                        break
                    if els[idx+1].tag == 'img':             
                        if idx > 0:
                            if els[idx-1].tag == 'img':
                                objs[cnt]['dest'], cnt = airport, cnt+1
                                objs[cnt]['orig'] = airport     
                        # first item is orig
                        else:
                            objs[cnt]['orig'] = airport
                    # multi-city
                    else:
                        objs[cnt]['dest'], cnt = airport, cnt+1
            cnt = 0
            for val in segs:
                seg = val.split(',')
                objs[cnt]['flight_no'].append(seg[1]+seg[3])
                objs[cnt]['segment'].append(
                    dict(
                        flight_no        = seg[1]+seg[3],
                        departure = dict(
                            airport_code = seg[4],
                            datetime     = datetime.datetime.strptime(seg[5],'%m/%d/%Y %I:%M:%S %p')
                        ), 
                        arrival = dict(
                            airport_code = seg[6],
                            datetime     = datetime.datetime.strptime(seg[7],'%m/%d/%Y %I:%M:%S %p')
                        )
                    )
                )
                if seg[6] != objs[cnt].get('dest'):
                    objs[cnt]['stops'].append(seg[6])
                else:
                    objs[cnt]['identifier'] = identifier
                    objs[cnt]['duration'] = '%s %s' % (dur[2],dur[4])
                    objs[cnt]['no_stops'] = len(objs[cnt]['stops'])
                    identifier = self._data_to_id(objs[cnt])                    
                    if identifier in dups:
                        objs[cnt]['duplicate'] = True
                    else:
                        dups.append(identifier)
                    cnt+=1    
            price = re.search("^\$(.*)\xa0total$", price).group(1).replace(',','')
            identifiers = [i['identifier'] for i in objs]
            identifiers.append(price)
            list_ids.append(identifiers)
            out.append(dict(details=objs,price=price))

        for path in list_ids:
            current_level = id_table
            mx = len(path)-1
            for idx, part in enumerate(path):
                if part not in current_level:
                    if idx != mx:
                        current_level[part] = {}
                    else:
                        current_level['price'] = part
                        break
                current_level = current_level[part]  
                                                      
        return (out, id_table)

    def _schedule_data(self, items, index):
        el = items.eq(index)
        fc = el.find('.FlightCell')
        dur = fc.find('li.SegmentDiv > span').text().split()
        
        attrs = str(fc.find('li.SegmentDiv a[title="Seats"]').attr('onclick')).split('&segs=')[1]
        segs = attrs.split('|')[:-1]

        obj = dict(
            dest      = el.attr('dest'),
            orig      = el.attr('orig'),
            no_stops  = el.attr('stops'),            
            duration  = '%s %s' % (dur[0],dur[2]),
            flight_no = [],
            segment   = [],
            stops     = []
        )  

        obj['prices'] = dict(
            coach = dict(
                lowest      = el.find('.BestDealColumn .Price').text()[1:],
                refundable = el.find('.FullFlexColumn .Price').text()[1:]
            ),
            first = dict(
                lowest      = el.find('.FirstClassDealColumn .Price').text()[1:],
                refundable = el.find('.FirstClassColumn .Price').text()[1:]
            )
        )

        for seg in segs:
            seg = seg.split(',')
            obj['flight_no'].append('AS'+seg[3])
            obj['stops'].extend([seg[4],seg[6]])
            obj['segment'].append(
                dict(
                    flight_no        = seg[3],
                    departure = dict(
                        airport_code = seg[4],
                        datetime     = datetime.datetime.strptime(seg[5],'%m/%d/%Y %I:%M:%S %p')
                    ), 
                    arrival = dict(
                        airport_code = seg[6],
                        datetime     = datetime.datetime.strptime(seg[7],'%m/%d/%Y %I:%M:%S %p')
                    )
                )
            )

        obj['stops'] = list(OrderedDict.fromkeys(obj['stops'][1:-1]))
        obj['identifier'] = self._data_to_id(obj, airline='AS')

        return obj

    def search(self, request, reservation={}):
        itinerary = reservation.get('itinerary')
        form = itinerary or request.form
        params = ['IsRoundTrip','IsOneWay','IsMultiCity','ReturnDate','CabinType']
        for i in range(4):
            for x in ['DepartureCity','DepartureDate','ArrivalCity']:
                params.append('%s%s'%(x,i+1))

        data = dict()
        for v in params:
            if form.get(v):
                data[v] = form.get(v)       

        key = ''.join([v for k, v in data.items()])
        r = cacheUtils.get(key)

        log.debug(data)
        
        if not r:
            r = requests.post(self.SHOP_URL, data=data)
            log.debug("No cached key. Searching Alaska.")
            cacheUtils.set(key, r)

        junk = re.compile(r'[\n\r\t]')     
        c = r.content       
        d = pq(junk.sub('',c))   

        out = []
        tables = d.find('.MatrixTable')
        try:
            # standard query by schedule
            if tables:
                for table in tables:
                    items = pq(table).find('.Option')        
                    out.append([self._schedule_data(items, i) for i, v in enumerate(items)])

                has_reservation, current_price = reservation.has_key('segment'), 0
                for idx, item in enumerate(out):
                    cabin = reservation['segment'][idx].get('class') if has_reservation else form.get('CabinType', 'coach').lower()
                    for val in item:
                        if val.has_key('prices'):
                            val['price'] = val.get('prices').get(cabin).get('lowest','refundable')
                        if has_reservation:
                            if val['identifier'] == reservation['segment'][idx].get('identifier'):
                                reservation['segment'][idx]['current'] = val
                                current_price += float(val['price'])
                if has_reservation:
                    reservation['current_price'] = current_price

                resp = dict(by_schedule=out, reservation=reservation)                    
            # special query by price
            else:
                log.debug("Coudn't find the schedule table. Trying price table.")
                table = d.find('#BundledTable')
                items = pq(table).find('.Option')        
                (out, ids) = self._price_data(items, data)
                resp = dict(by_price=out, id_table=json.dumps(ids))
        except Exception as e:
            log.error(e)
            raise FlashMessage("Hmm, we didn't find anything. There could be no flights or \
                            this may be a known issue we're working on.", category='danger')

        resp['reservation'] = reservation
        resp['data'] = security.json_encrypt(data)
        return resp














"""
form = dict(
    flightType='1',
    IsRoundTrip='false',
    IsOneWay='true',
    IsMultiCity='false',
    IsAwardReservation='false',
    AdultCount='1 Adult',
    ChildrenCount='0 Children',
    UMNRAnswer='',
    DepartureCity1='PDX',
    DepartureCity2='',
    DepartureCity3='',
    DepartureCity4='',
    ArrivalCity1='Kahului, HI (OGG-Kahului/Maui)',
    ArrivalCity2='',
    ArrivalCity3='',
    ArrivalCity4='',
    DepartureDate1='08/23/2014',
    DepartureDate2='03/01/2014',
    DepartureDate3='03/01/2014',
    DepartureDate4='03/01/2014',
    DepartureTime1='10am - 2pm',
    DepartureTime2='Anytime',
    DepartureTime3='Anytime',
    DepartureTime4='Anytime',
    ReturnDate='09/03/2014',
    ReturnTime='10am - 2pm',
    IncludeNearbyDepartureAirports='false',
    IncludeNearbyArrivalAirports='false',
    ShopAwardCalendar='false',
    ShopLowFareCalendar='false',
    CabinType='Coach',
    FareType='NoUpgradePreference',
    AwardOption='MilesOnly',
    DiscountCode='',
    ContractFareTypeKey='',
    ShowOnlyContractFares='false',
    ShowContractAndAllFares='false',
    ShoppingRequestModel = dict(
        AdultCount='1 Adult',
        ChildrenCount='0 Children',
        DepartureCity1='Portland, OR (PDX-Portland Intl.)',
        ArrivalCity1='Sacramento, CA (SMF-Metropolitan)',
        DepartureDate1='08/23/2014',
        DepartureTime1='10am - 2pm',
        DepartureCity2='From',
        ArrivalCity2='To',
        DepartureDate2='03/01/2014',
        DepartureTime2='Anytime',
        DepartureCity3='From',
        ArrivalCity3='To',
        DepartureDate3='03/01/2014',
        DepartureTime3='Anytime',
        DepartureCity4='From',
        ArrivalCity4='To',
        DepartureDate4='03/01/2014',
        DepartureTime4='Anytime',
        IncludeNearbyDepartureAirports='false',
        IncludeNearbyArrivalAirports='false',
        ReturnDate='09/03/2014',
        ReturnTime='10am - 2pm',
        ShopLowFareCalendar='false',
        ShopAwardCalendar='false',
        AwardOption='MilesOnly',
        CabinType='Coach',
        FareType='Coach',
    )
)""" 

#values = {'TravelerLastName':'Sherman','CodeOrNumber':'NRVCPP','Continue':'CONTINUE'}
#values = {'TravelerLastName':'Greisel','CodeOrNumber':'EVXDQD','Continue':'CONTINUE'}