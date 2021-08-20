import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class InterceptSpider(scrapy.Spider, BoilerPlateParser):
    name = 'intercept'
    allowed_domains = ['theintercept.com']
    start_urls = ['https://theintercept.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            try:
                item['title'] = soup.find('h1', class_='Post-title').text.strip()
            except:
                item['title'] = soup.find('h1', class_='Post-feature-title').text.strip()
            byline = soup.find('div', class_='PostByline-names')
            item['byline'] = re.sub('  +', ' ', byline.text.strip())

            date = soup.find('span', 'PostByline-date').text.strip()
            date = parser.parse(re.sub('  +', ' ', date))
            item['date'] = date

            root = soup.find('div', class_='PostContent')
            paragraphs = root.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'^/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                link = link.split('?')[0]
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
