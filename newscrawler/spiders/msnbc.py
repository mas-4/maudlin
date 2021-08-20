import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class MsnbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'msnbc'
    allowed_domains = ['www.msnbc.com']
    start_urls = ['https://www.msnbc.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', attrs={'class': re.compile(r'headline')}).text.strip()
            byline = soup.find('div', attrs={'class': re.compile(r'article-byline')})
            item['byline'] = re.sub('  +', ' ', byline.text.strip())

            date = soup.find('time', attrs={'itemprop': 'datePublished'})
            date = parser.parse(date.text.strip())
            item['date'] = date

            root = soup.find('div', attrs={'class': re.compile('article-body')})
            paragraphs = root.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'n\d+$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if '/author/' not in link:
                    yield response.follow(link, callback=self.parse)
