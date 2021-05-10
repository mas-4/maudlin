import scrapy
import re
from scrapy import signals
from time import sleep
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin


class DailybeastSpider(SeleniumMixin, scrapy.Spider, BoilerPlateParser):
    name = 'dailybeast'
    allowed_domains = ['www.thedailybeast.com']
    start_urls = ['https://www.thedailybeast.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find(
                'h1', attrs={'class': re.compile('__title')}).text.strip()
            item['byline'] = soup.find('h4', class_='Byline__name').text.strip()

            date = soup.find('time',
                             class_='PublicationTime__pub-time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='Body__content')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            self.driver.get(response.url)
            sleep(5)
            soup = BS(self.driver.page_source, 'lxml')
            attrs={'href': re.compile(r'ref=home')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            links = list(filter(lambda l: '/author/' not in l, links))
            for link in links:
                yield response.follow(link, callback=self.parse)
