import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class NypostSpider(scrapy.Spider, BoilerPlateParser):
    name = 'nypost'
    allowed_domains = ['nypost.com']
    start_urls = ['https://nypost.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile('postid')}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'p'
            attrs = {'class': 'byline'}
            byline = soup.find(tag, attrs=attrs).a
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'p'
            attrs = {'class': 'byline-date'}
            date = soup.find(tag, attrs)
            date = date.text.strip().split('|')[0]
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'entry-content'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
