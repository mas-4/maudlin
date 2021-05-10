import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class DailywireSpider(scrapy.Spider, BoilerPlateParser):
    name = 'dailywire'
    allowed_domains = ['www.dailywire.com']
    start_urls = ['https://www.dailywire.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1').text.strip()
            byline = soup.find('a', attrs={'href': re.compile(r'/author/')})
            item['byline'] = byline.text.strip()

            date = soup.find('time')
            date = parser.parse(date['datetime'])
            item['date'] = date

            root = soup.find('div', id='post-body-text')
            paragraphs = root.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile('/news/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
