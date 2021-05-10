import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class HillSpider(scrapy.Spider, BoilerPlateParser):
    name = 'hill'
    allowed_domains = ['thehill.com']
    start_urls = ['https://thehill.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', id='page-title').text.strip()
            byline = soup.find('span', class_='submitted-by').a.text.strip()
            item['byline'] = byline

            date = soup.find('span', class_='submitted-date').text.strip()
            date = parser.parse(date.replace('.', ':'))
            item['date'] = date

            story = soup.find('div', attrs={'class': 'field-item'})
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('div', id='main')
            links = []
            for a in root.find_all('a'):
                try:
                    links.append(a['href'])
                except:
                    continue

            for link in links:
                if '/shopping' not in link:
                    yield response.follow(link, callback=self.parse)
