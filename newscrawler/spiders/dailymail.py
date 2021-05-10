import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin

class DailymailSpider(scrapy.Spider, BoilerPlateParser, SeleniumMixin):
    name = 'dailymail'
    allowed_domains = ['www.dailymail.co.uk']
    start_urls = ['https://www.dailymail.co.uk/ushome/index.html']

    def parse(self, response):
        self.driver.get(response.url)
        soup = BS(self.driver.page_source, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            root = soup.find('div', class_='article-text')
            item['title'] = root.h2.text.strip()

            byline = root.find('p', attrs={'class': 'author-section byline-plain'})
            item['byline'] = byline.text.strip()

            date = root.find('span', attrs={'class':'article-timestamp article-timestamp-published'})
            date = date.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', attrs={'itemprop': 'articleBody'})
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/news/article-\d+/[^#]+$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
