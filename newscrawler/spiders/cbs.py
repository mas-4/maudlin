from newscrawler.models import Article
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class CbsSpider(scrapy.Spider, BoilerPlateParser):
    name = 'cbs'
    allowed_domains = ['www.cbsnews.com']
    start_urls = ['https://www.cbsnews.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)
            try:
                item['title'] = soup.find('h1', class_='content__title').text.strip()
            except:
                item['title'] = soup.find('h1', class_='title').text.strip()
            try:
                item['byline'] = soup.find('p', class_='content__meta--byline').text.strip()
            except:
                item['byline'] = soup.find('li', class_='correspondent-box').text.strip()

            try:
                date = soup.find('time')['datetime'].strip()
            except:
                date = soup.find('li', class_='date-box').text.strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('section', class_='content__body')
            if not story:
                story = soup.find('div', class_='content__body')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            links = []
            for section in soup.find_all('section'):
                if section['id'] == 'component-top-stories':
                    continue
                for a in section.find_all('a'):
                    if a['href'].startswith('http'):
                        links.append(a['href'])

            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if '/live/' in link or '/video/' in link:
                    continue
                yield response.follow(link, callback=self.parse)
