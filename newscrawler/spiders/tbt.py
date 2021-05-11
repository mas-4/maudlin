import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class TbtSpider(scrapy.Spider, BoilerPlateParser):
    name = 'tbt'
    allowed_domains = ['tampabay.com']
    start_urls = ['https://www.tampabay.com/']


    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            title = (soup.find('h1', class_='article__headline') or
                     soup.find('div', class_='opinion__headline'))
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
                yield response.follow(link, callback=self.parse)
