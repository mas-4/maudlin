import re
from newscrawler.models import Article
import scrapy
from scrapy import signals
from time import sleep
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin


class PoliticoSpider(SeleniumMixin, scrapy.Spider, BoilerPlateParser):
    name = 'politico'
    allowed_domains = ['www.politico.com']
    start_urls = ['https://www.politico.com/']
    special = 'https://www.politico.com/news/'

    def parse(self, response):
        self.driver.get(response.url)
        sleep(5)
        soup = BS(self.driver.page_source, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            title = soup.find('h2', class_='headline')
            if not title:
                title = soup.find('span', attrs={'itemprop': 'headline'})
            if not title:
                title = soup.find('header')
            item['title'] = title.text.strip()
            byline = soup.find('p', class_='story-meta__authors')
            if byline:
                byline = byline.span
            else:
                byline = soup.find('p', attrs={'rel': 'author'})
            if byline:
                item['byline'] = byline.text.strip()
            else:
                item['byline'] = None

            date = soup.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            paragraphs = []
            for box in soup.find_all('div', class_='story-text'):
                paragraphs.extend(box.find_all('p'))
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if '/video/' in link:
                    continue
                if '/cartoons/' in link:
                    continue
                yield response.follow(link, callback=self.parse)
