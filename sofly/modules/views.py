from flask import Blueprint, g, redirect, \
    render_template, request, session

from sofly.helpers import redirect_url
from sofly.utils.crawler import CrawlerUtils
from sofly.modules.users.views import User

module = Blueprint('base', __name__)

crawlerUtils = CrawlerUtils()

@module.route('/crawl')
def crawl():
    print request.args.get('token','')
    if request.args.get('token','') == 'mcHX47n8R3qe3z5bHuuWJGscWASapY2Aa9THDeSmraNh2vxskCSTy45qEvbuZkCZ':
        crawlerUtils.crawl()
    return redirect(redirect_url())
