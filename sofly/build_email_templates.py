# THESE ARE TEMP FOR EMAIL TEMPALTE BULDING
from jinja2 import Environment, FileSystemLoader
import os, premailer


@app.route('/email/<template>')
def email(template):  

    search_params = {u'IsRoundTrip': u'true', u'ReturnDate': u'03/25/2014', u'DepartureCity1': u'pdx', u'ArrivalCity1': u'sea', u'DepartureDate1': u'03/25/2014', u'CabinType': u'coach'}
    identifier = 'PDX201403250845SEA20140325093300480AS2128|SEA201403251605PDX20140325165200470AS2061'
    search = alaskaUtils.crawl(search_params)
    search.set_itinerary_by_identifier(identifier)
    itinerary = search.itineraries[0]
    #itinerary.price = search.get_price_by_identifier(identifier)

    template_dir = os.path.join(app.root_path, app.template_folder)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['duration'] = filters.duration
    env.filters['no_stops'] = filters.no_stops    
    env.globals['url_for'] = url_for
    
    template = env.get_template('email/%s.html' % template)
    
    subject = 'Fare Alert: '
    for flight in itinerary.flights:
        subject += '%s >> %s, %s' % (
                flight.origin,
                flight.destination,
                flight.depart
            )
    #if flight.get('inbound'):
    #    subject += ', Returning %s' % flight['inbound']['departure_date']
    html = template.render(dict(
        search_params = None,
        reservation = dict(paid = '453.50'),
        itinerary = itinerary
    ))
    #return html
    out = premailer.Premailer(html, 
            include_star_selectors=True,
            exclude_pseudoclasses=True
        ).transform()    
    #mailUtils.send_email('pdxandi@gmail.com', subject, out)
    return out

