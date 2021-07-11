from newscrawler.models import Article
import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class VoxSpider(scrapy.Spider, BoilerPlateParser):
    name = 'vox'
    allowed_domains = ['www.vox.com']
    start_urls = ['https://www.vox.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find(
                'h1', attrs={'class': re.compile(r'page-title')}).text.strip()
            item['byline'] = soup.find(
                'span', attrs={'class': re.compile('byline__author-name')}
            ).text.strip()

            date = soup.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='c-entry-content')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'data-analytics-link': 'article'}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
