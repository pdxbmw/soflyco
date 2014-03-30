from sofly import app
from flask import Markup
import humanize
import json

log = app.logger

@app.template_global('tagline')
def tagline():
    return Markup('The simplest way to get refunds on your \
        <a href="http://www.alaskaair.com/content/deals/special-offers/price-guarantee.aspx">Alaska Airline</a> flights')

@app.template_filter('apnumber')
def apnumber(arg):
    out = humanize.apnumber(arg)
    return out
    #return 'no' if out == '0' else out

@app.template_filter('airport_code')
def airport_code(arg):
    out = ''
    if type(arg) is not list:
        arg = [arg]
    for index, value in enumerate(arg):
        out += '<abbr class="airport-code" data-value="%s">%s</abbr>' % (value, value)
        if index != len(arg)-1:
            out += ', '
    return Markup(out)

@app.template_filter('duration')
def duration(arg):
    out = arg
    hours, minutes = int(arg[0:2]), int(arg[2:4])
    try:
        out = '{:01d}h {:01d}m'.format(hours, minutes)
    except Exception as e:
        log.error(e)
    return out

@app.template_filter('multi_label')
def multi_label(arg):
    if arg == 1:
        return 'First'
    elif arg == 2:
        return 'Second'
    elif arg == 3:
        return 'Third'
    elif arg == 4:
        return 'Fourth'

@app.template_filter('no_stops')
def no_stops(arg):
    arg = int(arg)
    out = 'Nonstop' if arg == 0 else '%s stop' % arg
    if arg > 1:
        out += 's'
    return out

@app.template_filter('pluralize')
def pluralize(arg):
    out = ''
    try:
        if len(arg) != 1:
            out = 's' 
    except:
        pass
    return out