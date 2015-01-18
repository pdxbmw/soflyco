#!/usr/local/bin/python
import os
import time

from multiprocessing import Process

from www import create_app
from www.utils.crawler import CrawlerUtils

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
crawler = CrawlerUtils(app)

def run():
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    server = Process(target=run)
    server.start()

    time.sleep(1)
    crawler.crawl()
    time.sleep(1)
    
    server.terminate()
    server.join()