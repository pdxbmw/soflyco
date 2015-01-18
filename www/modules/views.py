from flask import abort, Blueprint, g, redirect, \
    render_template, request, session

from www.helpers import redirect_url
from www.utils.crawler import CrawlerUtils
from www.modules.users.views import User

module = Blueprint('base', __name__)

crawlerUtils = CrawlerUtils()

@module.route('/crawl')
def crawl():
    print request.args.get('token','')
    if request.args.get('token','') == 'mcHX47n8R3qe3z5bHuuWJGscWASapY2Aa9THDeSmraNh2vxskCSTy45qEvbuZkCZ':
        crawlerUtils.crawl()
    return redirect(redirect_url())

@module.route('/<page>')
def page(page):
    # force 404 for debugging
    try:
        return render_template('%s.html' % page)
    except:
        abort(404)