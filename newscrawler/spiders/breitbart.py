import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class BreitbartSpider(scrapy.Spider, BoilerPlateParser):
    name = 'breitbart'
    allowed_domains = ['www.breitbart.com']
    start_urls = ['https://www.breitbart.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            root = soup.find('article', class_='the-article')
            item['title'] = root.find('h1').text.strip()
            item['byline'] = soup.find(
                'div', class_='header_byline').address.text.strip()

            date = soup.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='entry-content')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        elif response.url == self.start_urls[0]:
            attrs={'href': re.compile(r'/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                link = link.split('#')[0].strip()
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                else:
                    yield response.follow(link, callback=self.parse)
