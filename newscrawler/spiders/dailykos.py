import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class DailykosSpider(scrapy.Spider, BoilerPlateParser):
    name = 'dailykos'
    allowed_domains = ['www.dailykos.com']
    start_urls = ['https://www.dailykos.com/']


    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'div'
            attrs = {'class': 'story-title heading'}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'span'
            attrs = {'class': 'author-name'}
            byline = soup.find(tag, attrs=attrs)
            if byline:
                byline = re.sub('  +', ' ', byline.a.text.strip()) if byline else None

            tag = 'span'
            attrs = {'class': 'timestamp'}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'story-column'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/stories/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
