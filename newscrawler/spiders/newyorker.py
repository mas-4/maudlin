from newscrawler.models import Article
import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class NewyorkerSpider(scrapy.Spider, BoilerPlateParser):
    name = 'newyorker'
    allowed_domains = ['newyorker.com']
    start_urls = ['https://www.newyorker.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find(
                'h1', attrs={'data-testid': 'ContentHeaderHed'}).text.strip()

            byline = soup.find('a', class_='byline__name-link')
            item['byline'] = byline.text.strip()

            date = soup.find(
                'time',
                attrs={'data-testid': 'ContentHeaderPublishDate'}).text.strip()
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='article__body')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'data-component-type': 'recirc-river', 'href': re.compile('^/') }
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
