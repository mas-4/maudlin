from newscrawler.models import Article
import re
import scrapy
from time import sleep
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin
from dateutil import parser


class TimeSpider(SeleniumMixin, scrapy.Spider, BoilerPlateParser):
    name = 'time'
    allowed_domains = ['time.com']
    start_urls = ['https://time.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            self.driver.get(response.url)
            sleep(5)
            soup = BS(self.driver.page_source, 'lxml')
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': 'headline'}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'a'
            attrs = {'class': 'author-name'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'div'
            attrs = {'class': re.compile('timestamp published-date')}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            try:
                date = parser.parse(date)
            except:
                date = date.split('Originally published:')[-1].strip()

            tag = 'div'
            attrs = {'id': 'article-body'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'^/\d{7}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
