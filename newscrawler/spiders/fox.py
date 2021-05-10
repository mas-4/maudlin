import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser

CLASS = 'article-body'

class FoxSpider(scrapy.Spider, BoilerPlateParser):
    name = 'fox'
    allowed_domains = ['feeds.foxnews.com', 'www.foxnews.com']
    start_urls = ['http://feeds.foxnews.com/foxnews/latest']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if 'www' in response.url:
            item = self.prepopulate_item(response)

            item['title'] = response.css('h1.headline::text').get()
            # fragile
            item['byline'] = response.css('.author-byline > span:nth-child(2) > span:nth-child(1) > a:nth-child(1)::text').get()

            date = soup.find('meta', attrs={'name': 'dc.date'})
            if date['content']:
                date = parser.parse(date['content'])
                item['date'] = date

            text = soup.find('div', class_=CLASS)
            if not text:
                return None

            paragraphs = text.find_all('p')
            # filter out ad paragraphs, which are always all caps
            paragraphs = list(filter(lambda l: l.text.strip().upper() != l.text.strip(), paragraphs))
            text = self.joinparagraphs(paragraphs)

            # replace nbsp
            item['text'] = text.replace('\xa0', ' ')

            yield item
        for a in response.css('guid::text'):
            yield response.follow(a, callback=self.parse)
