from flask import Blueprint, Markup, current_app

import humanize
import json

module = Blueprint('filters', __name__)

# Globals
@module.app_template_global('policylink')
def policylink(text):
    return Markup('<a href="http://www.alaskaair.com/content/deals/special-offers/price-guarantee.aspx">%s</a>' % text)

@module.app_template_global('refundurl')
def refundurl():
    return Markup('https://www.alaskaair.com/booking/ssl/garr/GuaranteedAirfare.aspx')  

@module.app_template_global('tagline')
def tagline():
    return Markup('Get the lowest price on your ' + policylink('Alaska Airlines') + ' flights')

# Filters
@module.app_template_filter('apnumber')
def apnumber(arg):
    out = humanize.apnumber(arg)
    return out
    #return 'no' if out == '0' else out

@module.app_template_filter('no_for_zero')
def no_for_zero(arg):
    return 'no' if arg == '0' else arg    

@module.app_template_filter('airport_code')
def airport_code(arg):
    out = ''
    if type(arg) is not list:
        arg = [arg]
    for index, value in enumerate(arg):
        out += '<abbr class="airport-code" data-value="%s">%s</abbr>' % (value, value)
        if index != len(arg)-1:
            out += ', '
    return Markup(out)

@module.app_template_filter('duration')
def duration(arg):
    out = arg
    hours, minutes = int(arg[0:2]), int(arg[2:4])
    try:
        out = '{:01d}h {:01d}m'.format(hours, minutes)
    except Exception as e:
        current_app.logger.error(e)
    return out

@module.app_template_filter('multi_label')
def multi_label(arg):
    if arg == 1:
        return 'First'
    elif arg == 2:
        return 'Second'
    elif arg == 3:
        return 'Third'
    elif arg == 4:
        return 'Fourth'

@module.app_template_filter('no_stops')
def no_stops(arg):
    arg = int(arg)
    out = 'Nonstop' if arg == 0 else '%s stop' % arg
    if arg > 1:
        out += 's'
    return out

@module.app_template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    out = singular
    try:
        if int(number) != 1:
            out = plural
    except:
        pass
    return out