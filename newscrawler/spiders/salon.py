import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class SalonSpider(scrapy.Spider, BoilerPlateParser):
    name = 'salon'
    allowed_domains = ['www.salon.com']
    start_urls = ['https://www.salon.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('section', class_='title-container').h1.text.strip()

            byline = soup.find('div', class_='writer_info_wrapper')
            item['byline'] = byline.h5.a.text.strip()

            date = byline.h6.text.strip().strip('Published ')\
                .replace('(', '').replace(')', '')
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('article')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile(r'\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
