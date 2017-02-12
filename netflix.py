from lxml import html
import requests

class netflix:
  def __init__(self, content_id):
    movieID = content_id.split('/')[-1]
    print("ID : " + movieID)
    page = requests.get('http://www.allflicks.dk/film/'+movieID)
    self.tree = html.fromstring(page.content)
    
  def title(self):
    title = self.tree.xpath('//div[@id="post-8"]/h1/text()')
    title, app = title[0].split(" - ")
    return title
    
    
