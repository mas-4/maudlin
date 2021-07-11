from newscrawler.models import Article
import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class AtlanticSpider(scrapy.Spider, BoilerPlateParser):
    name = 'atlantic'
    allowed_domains = ['www.theatlantic.com']
    start_urls = ['https://www.theatlantic.com/']


    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile('ArticleTitle')}
            title = soup.find(tag, attrs=attrs)
            if not title:
                title = soup.find('h1', class_='hed')
            title = title.text.strip()

            tag = 'a'
            attrs = {'class': re.compile('ArticleByline')}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'time'
            attrs = {'class': re.compile('ArticleTimestamp')}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            try:
                date = parser.parse(date)
            except:
                tag = 'meta'
                attrs = {'property': 'article:published_time'}
                date = soup.find(tag, attrs)
                date = date['content'].strip()
                date = parser.parse(date)


            tag = 'section'
            attrs = {'class': re.compile('ArticleBody')}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)
            if not date:
                date = paragraphs[0].text.split(' on ')[-1]
                date = parser.parse(date.strip('.'))

            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/archive/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
