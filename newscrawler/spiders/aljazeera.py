import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class AljazeeraSpider(scrapy.Spider, BoilerPlateParser):
    name = 'aljazeera'
    allowed_domains = ['aljazeera.com']
    start_urls = ['https://www.aljazeera.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'header'
            attrs = {'class': 'article-header'}
            title = soup.find(tag, attrs=attrs).h1
            title = title.text.strip()

            tag = 'div'
            attrs = {'class': 'article-author-name'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'div'
            attrs = {'class': 'article-dates'}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': re.compile('all-content')}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{1,2}/\d{1,2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
