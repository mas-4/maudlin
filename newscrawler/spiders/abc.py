import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class AbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'abc'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['https://abcnews.go.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='Article__Headline__Title').text.strip()
            item['byline'] = soup.find('span', class_='Byline__Author').text.strip()

            date = soup.find('div', class_='Byline__Meta Byline__Meta--publishDate').text.strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('section', class_='Article__Content story')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            links = soup.find_all('a', attrs={'class': 'AnchorLink', 'href': re.compile(r'http.*\d?id=\d+$')})

            for link in links:
                if Article.query.filter(Article.url.endswith(link['href'])).first():
                    continue
                yield response.follow(link['href'], callback=self.parse)
