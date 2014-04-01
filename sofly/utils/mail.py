from flask import g, render_template, url_for

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from jinja2 import Environment, FileSystemLoader

import os
import premailer
import smtplib

class MailUtils(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # setting explicitly for offline crawling
        self.template_dir = os.path.join(os.environ.get('BASE_DIR',''), 'templates')        
        self.MAIL_HOST = app.config['MAIL_HOST']
        self.MAIL_USERNAME = app.config['MAIL_USERNAME'] 
        self.MAIL_PASSWORD = app.config['MAIL_PASSWORD']

    def create_email_MIME(self, from_email, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        text = msg.as_string()
        return text   
        
    def watching_template(self, request, itinerary):
        itinerary.price = request.form.get('price')
        context = dict(
            itinerary = itinerary, 
            reservation = dict(
                paid = request.form.get('paid')
            )
        )
        return self.render_template('email/watching.html', context)

    def render_template(self, tmpl, template_values):
        from sofly.modules import filters
        env = Environment(loader=FileSystemLoader(self.template_dir))
        
        env.filters['duration'] = filters.duration
        env.filters['no_stops'] = filters.no_stops
        env.globals['tagline'] = filters.tagline
        env.globals['url_for'] = url_for

        template = env.get_template(tmpl)
        html = template.render(**template_values)
        return premailer.Premailer(html, 
                    include_star_selectors=True,
                    exclude_pseudoclasses=True
                ).transform()   

    def send_activation_email(self, user=None, **kwargs):
        from sofly import helpers
        user = user or g.user
        url = helpers.get_activation_link(user.id) 
        html = self.render_template('email/welcome.html', dict(activate_url=url))
        self.send_email(user.email, 'Welcome to SoFly!', html)
        return url

    def send_email(self, to_email, subject, body, **kwargs):
        print (self.MAIL_HOST, self.MAIL_USERNAME, self.MAIL_PASSWORD)
        from_email = kwargs.get('from_email', 'SoFly! <admin@sofly.co>')
        text = self.create_email_MIME(from_email, to_email, subject, body)
        server = smtplib.SMTP_SSL(self.MAIL_HOST, timeout=10)
        server.ehlo()
        server.login(self.MAIL_USERNAME, self.MAIL_PASSWORD)
        server.sendmail(from_email, to_email, text)
        server.quit() 

    def send_fare_alert(self, watcher, search):
        itinerary = search.itineraries[0]
        subject = 'Fare Alert: '
        for flight in itinerary.flights:
            subject += '%s >> %s, %s' % (
                    flight.origin,
                    flight.destination,
                    flight.depart
                )       
        claim_link = helpers.get_claim_link(itinerary.identifier, watcher.email, itinerary.price)
        context = dict(
            claim_link = claim_link,
            itinerary = itinerary,
            reservation = watcher.reservation,
            search_params_encoded = search.search_params_encoded
        )
        html = self.render_template('email/fare_alert.html', context)
        if html:   
            self.send_email(watcher.email, subject, html)
        else:
            print "Error. No fare alert sent."        