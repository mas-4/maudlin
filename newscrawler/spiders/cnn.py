import scrapy
from dateutil import parser
from scrapy.linkextractors import LinkExtractor
from newscrawler.items import NewscrawlerItem
from bs4 import BeautifulSoup as BS

CLASS = 'afe4286c'

class CnnSpider(scrapy.Spider):
    name = 'cnn'
    allowed_domains = ['cnn.com']
    start_urls = ['http://lite.cnn.com/en']


    def parse(self, response):
        item = NewscrawlerItem()
        if response.url != self.start_urls[0]:
            item['agency'] = 'CNN'
            item['start'] = self.start_urls[0]
            item['url'] = response.url
            item['title'] = response.css('h2::text').get()
            item['byline'] = response.css('#byline::text').get()
            date = response.css('#published\ datetime::text').get()
            date = ''.join(date.split(':')[1:]).strip()
            date = parser.parse(date)
            item['date'] = date
            soup = BS(response.text, 'lxml')
            article = soup.find('div', class_=CLASS)
            paragraphs = article.find_all('p', id=None)
            text = []
            for p in paragraphs:
                text.append(p.text.strip())
            item['text'] = '\n'.join(text)
            yield item

        for article in response.css('li > a::attr(href)'):
            yield response.follow(article, callback=self.parse)
