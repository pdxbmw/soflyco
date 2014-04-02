#!/usr/local/bin/python
from sofly import create_app
from sofly.utils.crawler import CrawlerUtils
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
crawler = CrawlerUtils(app)

if __name__ == "__main__":
    crawler.crawl()