from newscrawler.models import Article
import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class HillSpider(scrapy.Spider, BoilerPlateParser):
    name = 'hill'
    allowed_domains = ['thehill.com']
    start_urls = ['https://thehill.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', id='page-title').text.strip()
            byline = soup.find('span', class_='submitted-by')
            if byline:
                item['byline'] = byline.text.strip()
            else:
                item['byline'] = None

            date = soup.find('span', class_='submitted-date')
            if date:
                date = parser.parse(date.text.strip().replace('.', ':'))
            else:
                date = soup.find('meta', attrs={'property': 'article:published_time'})['content']
                date = parser.parse(date)
            item['date'] = date

            story = soup.find('div', attrs={'class': 'field-items'})
            paragraphs = story.find_all('p')
            if paragraphs:
                text = self.joinparagraphs(paragraphs)
                item['text'] = text
            else:
                item['text'] = story.text.strip().replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile('/\d{6}[-0-9a-z]+$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if 'shopping' not in link:
                    yield response.follow(link, callback=self.parse)
