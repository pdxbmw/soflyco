from flask import g, render_template, url_for

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from jinja2 import Environment, FileSystemLoader

from sofly import app, security
from sofly.apps.common import filters, helpers

import os
import premailer
import smtplib

class MailUtils(object):
    USERNAME = 'admin@sofly.co'
    PASSWORD = 'dGMPyJ2a7%HszA^ga6@D'
    HOST = 'smtp.zoho.com:465'

    def __init__(self):
        pass  

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
        template_dir = os.path.join(app.root_path, app.template_folder)
        
        env = Environment(loader=FileSystemLoader(template_dir))
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
        user = user or g.user
        url = helpers.get_activation_link(user.id) 
        html = self.render_template('email/welcome.html', dict(activate_url=url))
        self.send_email(user.email, 'Welcome to SoFly!', html)
        return url

    def send_email(self, to_email, subject, body, **kwargs):
        from_email = kwargs.get('from_email', 'SoFly! <admin@sofly.co>')
        text = self.create_email_MIME(from_email, to_email, subject, body)
        server = smtplib.SMTP_SSL(self.HOST, timeout=10)
        server.ehlo()
        server.login(self.USERNAME, self.PASSWORD)
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