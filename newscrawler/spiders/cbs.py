import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class CbsSpider(scrapy.Spider, BoilerPlateParser):
    name = 'cbs'
    allowed_domains = ['www.cbsnews.com']
    start_urls = ['https://www.cbsnews.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='content__title').text.strip()
            item['byline'] = soup.find('p', class_='content__meta--byline').text.strip()

            date = soup.find('time')['datetime'].strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('section', class_='content__body')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            links = []
            for section in soup.find_all('section'):
                if section['id'] == 'component-top-stories':
                    continue
                for a in section.find_all('a'):
                    if a['href'].startswith('http'):
                        links.append(a['href'])

            for link in links:
                yield response.follow(link, callback=self.parse)
