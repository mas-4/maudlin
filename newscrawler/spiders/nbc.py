import re
from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class NbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'nbc'
    allowed_domains = ['www.nbcnews.com']
    start_urls = ['https://www.nbcnews.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            attrs = {'class': re.compile(r'headline')}
            item['title'] = soup.find('h1', attrs=attrs).text.strip()

            date = soup.find('time')['datetime'].strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('div', class_='article-body__content')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('div', class_='layout-grid-item')
            links = []
            for a in root.find_all('a'):
                try:
                    links.append(a['href'])
                except:
                    continue
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if '/video/' in link:
                    continue
                if '/live/' in link:
                    continue
                yield response.follow(link, callback=self.parse)
