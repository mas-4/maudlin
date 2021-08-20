import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class TbtSpider(scrapy.Spider, BoilerPlateParser):
    name = 'tbt'
    allowed_domains = ['tampabay.com']
    start_urls = ['https://www.tampabay.com/']


    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            title = (soup.find('h1', class_='article__headline') or
                     soup.find('div', class_='opinion__headline') or
                     soup.find('h1', class_='balance-text'))
            item['title'] = title.text.strip()
            byline = soup.find('a', class_=re.compile(r'article__byline--name'))
            if not byline:
                byline = soup.find('div', class_='opinion__byline')
            if byline:
                item['byline'] = re.sub('  +', ' ', byline.text.strip())

            date = soup.find('div', class_='timestamp--published').span
            date = parser.parse(date['title'])
            item['date'] = date

            root = soup.find('article', id='articleBody')
            paragraphs = root.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                link = link.split('?')[0]
                if Article.query.filter(Article.url.like('%' + link + '%')).first():
                    continue
                yield response.follow(link, callback=self.parse)
