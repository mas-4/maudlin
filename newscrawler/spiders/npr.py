from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article

CLASS = 'paragraphs-container'


class NprSpider(scrapy.Spider, BoilerPlateParser):
    name = 'npr'
    allowed_domains = ['text.npr.org']
    start_urls = ['https://text.npr.org/']

    def parse(self, response):
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = response.css('h1.story-title::text').get()
            item['byline'] = response.css('.story-head > p:nth-child(2)::text').get()

            date = response.css('.story-head > p:nth-child(3)::text').get()
            if not date:
                return None
            date = date.replace('• ', '')

            date = parser.parse(date)
            item['date'] = date

            soup = BS(response.text)
            container = soup.find('div', class_=CLASS)
            paragraphs = container.find_all('p', id=None)
            item['text'] = self.joinparagraphs(paragraphs)

            if len(item['text']) > 100:
                yield item

        for a in response.css('li > a::attr(href)'):
            link = a.get()
            if Article.query.filter(Article.url.endswith(link)).first():
                continue
            yield response.follow(link, callback=self.parse)
