import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article

headers = {
    'User-Agent': 'python-requests/2.25.1',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

class WapoSpider(scrapy.Spider, BoilerPlateParser):
    name = 'wapo'
    allowed_domains = ['www.washingtonpost.com']
    start_urls = ['https://www.washingtonpost.com/']

    def start_requests(self):
        return [scrapy.Request(self.start_urls[0],
                               callback=self.parse,
                               headers=headers)]

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', id='main-content').text.strip()

            byline = soup.find('span', attrs={'data-sc-c': 'author'})
            item['byline'] = byline.text.strip()

            date = soup.find('meta', attrs={'property':'article:published_time'})['content'].strip()
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='article-body')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile(r'^https://www.washingtonpost.com/.*story\.html$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse, headers=headers)
