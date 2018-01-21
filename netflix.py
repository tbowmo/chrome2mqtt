""" Netflix helping module """

from lxml import html
import requests

class Netflix:
    """ Netflix title scraping """
    def __init__(self, content_id):
        try:
            movie_id = content_id.split('/')[-1]
            page = requests.get('http://www.allflicks.dk/film/'+movie_id)
            self.tree = html.fromstring(page.content)
        except Exception:
            pass

    def title(self):
        """ Returns title of the showing media """
        try:
            title = self.tree.xpath('//div[@id="post-8"]/h1/text()')
            title, app = title[0].split(" - ")
        except Exception:
            title = "N/A"
        return title
