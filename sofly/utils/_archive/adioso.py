from datetime import datetime, timedelta
from pyquery import PyQuery as pq
from random import choice, randint
import requests

"""



    CURRENTLY UNUSED




"""

class FormatUtils(object):
    
    def _datetime(self, obj):        
        o_d_dt, o_a_dt = obj['o_d_dt'].split('-'), obj['o_a_dt'].split('-')
        o_d_tm, o_a_tm = obj['o_d_tm'].split(':'), obj['o_a_tm'].split(':')
        log.debug((o_d_dt, o_d_tm, o_a_dt, o_a_tm))
        return (
            datetime(int(o_d_dt[0]), int(o_d_dt[1]), int(o_d_dt[2]), int(o_d_tm[0]), int(o_d_tm[1])),
            datetime(int(o_a_dt[0]), int(o_a_dt[1]), int(o_a_dt[2]), int(o_a_tm[0]), int(o_a_tm[1]))
        )    




class AdiosoUtils(object):   
    """

        Adioso.com utilties

    """    
    BASE_URL = 'http://ajax%s.adioso.com/api/itinerary_summaries.html?q='%randint(1,8)
    
    def __init__(self):
        pass

    def _stops(self, el, start, end):
        stops, started = [], start if type(start) is bool else False
        items = el.find('.trip_segments .to .airport_code')
        for index, item in enumerate(items):
            text = items.eq(index).text()
            if text == start: started = True; continue
            if not started: continue
            if text == end: break
            stops.append(text)
        return (', ').join(stops)
    #
    def _flight_data(self, items, index):
        el = items.eq(index)
        i, o = el.find('.inbound'), el.find('.outbound')
        i_a, i_d = i.find('.arrival'), i.find('.departure')
        o_a, o_d = o.find('.arrival'), o.find('.departure')
        i_t, o_t = el.find('.segment:first'), el.find('.segment:last')
        dest, origin = el.attr('data-dest-code'), el.attr('data-origin-code')
        obj = {                       
            'outbound': {
                'date'             : el.attr('data-outbound-date'),
                'departure_date'   : o.find('.departure_date').text(),
                'duration'         : o.find('.duration').text().strip(),
                'flight_no'        : o_t.find('.flightNo').text().strip(),
                'no_stops'         : o.find('.stops').text().strip(),
                'stops'            : self._stops(el, True, dest),
                'arrival' : {
                    'airport_code' : dest,
                    'destination'  : o_a.find('.destination').text(),
                    'arrive'       : o_a.find('.arrive').text(),
                    'ampm'         : o_a.find('.ampm').text()
                },
                'departure' : {
                    'airport_code' : o_d.find('.airport_code').text(),
                    'origin'       : o_d.find('.origin').text(),
                    'depart'       : o_d.find('.depart').text(),
                    'ampm'         : o_d.find('.ampm').text()
                }
            },
            'expires'              : el.attr('data-outbound-date'),
            'identifier'           : el.attr('data-identifier'),
            'price'                : el.attr('data-localized-cost'),
        }  
        if len(i):
             obj['inbound'] = {
                'date'             : el.attr('data-outbound-date'),
                'departure_date'   : i.find('.departure_date').text(),
                'duration'         : i.find('.duration').text().strip(),
                'flight_no'        : i_t.find('.flightNo').text().strip(),
                'no_stops'         : i.find('.stops').text().strip(),
                'stops'            : self._stops(el, dest, origin),
                'arrival' : {
                    'airport_code' : origin,
                    'origin'       : i_a.find('.origin').text(),
                    'arrive'       : i_a.find('.arrive').text(),
                    'ampm'         : i_a.find('.ampm').text()
                },
                'departure' : {
                    'airport_code' : i_d.find('.airport_code').text(),
                    'destination'  : i_d.find('.destination').text(),
                    'depart'       : i_d.find('.depart').text(),
                    'ampm'         : i_d.find('.ampm').text()
                }
            }    
        obj['encrypted'] = security.json_encrypt(obj)
        return obj

    def id_to_qs(self, id):

        formatUtils = FormatUtils()

        o = []
        segments = id.split('|')
    
        for segment in segments:
            d = re.sub( r'([A-Z]{1,3})', r' \1', segment).split()
            # standard format
            flight = dict(    
                o_d_ac  = d[0][:3],
                o_d_dt  = '%s-%s-%s' % (d[0][3:7], d[0][7:9], d[0][9:11]),
                o_d_tm  = '%s:%s'    % (d[0][11:13], d[0][13:15]),
                o_a_ac  = d[1][:3],
                o_a_dt  = '%s-%s-%s' % (d[1][3:7], d[1][7:9], d[1][9:11]),
                o_a_tm  = '%s:%s'    % (d[1][11:13], d[1][13:15]),
                o_fn    = d[2]
            )
            o.append(flight)
    
        dpt, rtn = o[0], o[len(o)-1]        
        
        qs = {
            'from'      : dpt['o_d_ac'],
            'to'        : rtn['o_d_ac'],
            'start'     : dpt['o_d_dt'],
            'end'       : rtn['o_d_dt'],
            'start_time': formatUtils._datetime(dpt),
            'end_time'  : formatUtils._datetime(rtn)
        }

        log.debug(qs)

        return qs

    def qs_to_q(self, qs):
        
        def airport_code(s):
            try:
                f = s.split('(')
                return f[1][:3] if len(f) == 2 else s
            except AttributeError:
                return s

        def format_date(s):
            return '{0}-{1}'.format(calendar.month_name[int(s[5:7])], s[8:10].lstrip('0'))

        def _format_datetime(o,t):
            _ds,_de = (o[0]+timedelta(minutes=-1)),(o[0]+timedelta(minutes=1))
            _as,_ae = (o[1]+timedelta(minutes=-1)),(o[1]+timedelta(minutes=1))
            out = {
                '_departure_start_time_hour'   : _ds.hour,
                '_departure_start_time_minute' : _ds.minute,
                '_departure_end_time_hour'     : _de.hour,
                '_departure_end_time_minute'   : _de.minute,
                '_arrival_start_time_hour'     : _as.hour,
                '_arrival_start_time_minute'   : _as.minute,
                '_arrival_end_time_hour'       : _ae.hour,
                '_arrival_end_time_minute'     : _ae.minute
            }
            return '&'.join(['%s%s=%s'%(t,k,v) for k,v in out.items()])            

        start, end = qs.get('start'), qs.get('end')
        is_rt = int(qs.get('round_trip',1)) or start != end

        q = '%s+to+%s+%s%s&segments_filter_max=%s&class_of_service=%s&start=%s&end=%s&ccode=US&backend_to_use=%s&carrier_show_only=AS&' % (
            airport_code(qs.get('from')), 
            airport_code(qs.get('to')), 
            format_date(start),
            '+return+   %s' % format_date(end) if is_rt else '',
            qs.get('segments_filter_max',''),
            qs.get('class_of_service','0'),
            start,
            start,
            choice(['expediaapi'])
        )     

        if qs.get('start_time'):
            q += _format_datetime(qs.get('start_time'), 'outbound')+'&'
            
        if qs.get('end_time'):
            q += _format_datetime(qs.get('end_time'), 'inbound')

        return q

    def flights(self, q):
        log.debug(self.BASE_URL+q)

        if cacheUtils.get(q):
            log.debug('Found Adioso search in cache.')        
            c = cacheUtils.get(q)
        else:
            r = requests.get(self.BASE_URL+q)
            c = r.content
            log.debug('Caching Adioso request.')
            
        cacheUtils.set(q, c, time=3600)                     
        junk = re.compile(r'[\n\r\t]')            
        d = pq(junk.sub('',c))   

        log.debug(d)
        
        items = d.find('.itinerary_summary')
        return [self._flight_data(items, i) for i, v in enumerate(items)]

    def query_string(self, request, **kwargs):
        qs = kwargs.get('qs') or request.form or request.args
        return self.qs_to_q(qs)
