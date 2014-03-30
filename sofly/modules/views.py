from flask import Blueprint, g, redirect, \
    render_template, request, session

from sofly.helpers import redirect_url
from sofly.utils.crawler import CrawlerUtils
from sofly.modules.users.views import User

module = Blueprint('base', __name__)

crawlerUtils = CrawlerUtils()

@module.before_request
def before_request():
    """
    Pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.objects.get(id=ObjectId(session['user_id']))

@module.route('/')
def index():
    return render_template('index.html')   

@module.route('/crawl')
def crawl():
    print request.args.get('token','')
    if request.args.get('token','') == 'mcHX47n8R3qe3z5bHuuWJGscWASapY2Aa9THDeSmraNh2vxskCSTy45qEvbuZkCZ':
        crawlerUtils.crawl()
    return redirect(redirect_url())
