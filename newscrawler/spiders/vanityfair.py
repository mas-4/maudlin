import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class VanityfairSpider(scrapy.Spider, BoilerPlateParser):
    name = 'vanityfair'
    allowed_domains = ['vanityfair.com']
    start_urls = ['https://www.vanityfair.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'data-testid': 'ContentHeaderHed'}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'span'
            attrs = {'data-testid': 'BylineName'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'time'
            attrs = {'data-testid': 'ContentHeaderPublishDate'}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'article__body'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'news/\d{4}')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
