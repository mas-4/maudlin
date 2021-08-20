import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class ForeignpolicySpider(scrapy.Spider, BoilerPlateParser):
    name = 'foreignpolicy'
    allowed_domains = ['foreignpolicy.com']
    start_urls = ['https://foreignpolicy.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='hed').text.strip()
            byline = soup.find('div', class_='author-bio')
            if not byline:
                byline = soup.find('address', class_='author-list')
            item['byline'] = re.sub('  +', ' ', byline.text.strip())

            date = soup.find('time')
            date = parser.parse(date['datetime'])
            item['date'] = date

            root = soup.find('div', class_='post-content-main')
            paragraphs = root.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'^(https|/).*/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                link = link.split('?')[0]
                if Article.query.filter(Article.url.like('%' + link + '%')).first():
                    continue
                else:
                    print("Not found, <"+link + ">")
                    yield response.follow(link, callback=self.parse)
