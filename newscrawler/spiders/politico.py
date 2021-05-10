import scrapy
from scrapy import signals
from time import sleep
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin


class PoliticoSpider(SeleniumMixin, scrapy.Spider, BoilerPlateParser):
    name = 'politico'
    allowed_domains = ['www.politico.com']
    start_urls = ['https://www.politico.com/']
    special = 'https://www.politico.com/news/'

    def parse(self, response):
        self.driver.get(response.url)
        sleep(5)
        soup = BS(self.driver.page_source, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h2', class_='headline').text.strip()
            item['byline'] = soup.find('p', class_='story-meta__authors')\
                .span.text.strip()

            date = soup.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            paragraphs = []
            for box in soup.find_all('div', class_='story-text'):
                paragraphs.extend(box.find_all('p'))
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            links = soup.find_all('a')
            for a in links:
                try:
                    if a['href'].startswith(self.special):
                        yield response.follow(a['href'], callback=self.parse)
                except:
                    continue
