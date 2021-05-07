import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class BbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'bbc'
    allowed_domains = ['bbc.com', 'bbc.co.uk']
    start_urls = ['http://feeds.bbci.co.uk/news/rss.xml']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = response.css('#main-heading::text').get()
            item['byline'] = None # No byline on the bbc

            date = soup.find('time')
            date = parser.parse(date['datetime'])
            item['date'] = date

            paragraphs = soup.find_all('div', attrs={'data-component': 'text-block'})
            item['text'] = self.joinparagraphs(paragraphs)
            if not item['text']:
                yield None
            else:
                yield item

        if response.url == self.start_urls[0]:
            for a in soup.find_all('guid'):
                yield response.follow(a.text, callback=self.parse)
