from datetime import date as dt
import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


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

            try:
                date = soup.find('label', attrs={'for': 'dateToggle'}).text.strip()
                date = parser.parse(date.replace('.', ':'))
                item['date'] = date
            except:
                date = soup.find('meta', attrs={'property': 'article:published_time'})['content']
                date = parser.parse(date)
                item['date'] = date

            story = soup.find('div', attrs={'class': re.compile('article-body')})
            if not story:
                story = soup.find('div', class_='from-content-api')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

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
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if (str(dt.today().year) in link
                        and '/live/' not in link
                        and '/video/' not in link
                        and '/gallery/' not in link):
                    yield response.follow(link, callback=self.parse)
