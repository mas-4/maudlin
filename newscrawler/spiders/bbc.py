import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class BbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'bbc'
    allowed_domains = ['bbc.com']
    start_urls = ['https://www.bbc.com/']

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
            yield item

        if response.url == self.start_urls[0]:
            for a in soup.find('div', id='orb-modules')\
                    .find_all('a', class_='top-list-item__link'):
                yield response.follow(a['href'], callback=self.parse)
