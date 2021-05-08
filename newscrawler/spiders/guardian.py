import re
import scrapy
from datetime import date as dt
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class GuardianSpider(scrapy.Spider, BoilerPlateParser):
    name = 'guardian'
    allowed_domains = ['www.theguardian.com']
    start_urls = ['https://www.theguardian.com/us']


    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1').text.strip()
            byline = soup.find('a', attrs={'rel': 'author'})
            item['byline'] = byline.text.strip() if byline else None

            date = soup.find('label', attrs={'for': 'dateToggle'}).text.strip()
            date = parser.parse(date.replace('.', ':'))
            item['date'] = date

            story = soup.find('div', attrs={'class': re.compile('article-body')})
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('div', class_='facia-page')
            links = []
            for a in root.find_all('a'):
                try:
                    links.append(a['href'])
                except:
                    continue

            for link in links:
                if (str(dt.today().year) in link
                        and '/live/' not in link
                        and '/video/' not in link):
                    yield response.follow(link, callback=self.parse)
