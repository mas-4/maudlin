import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

class HuffpostSpider(scrapy.Spider, BoilerPlateParser):
    name = 'huffpost'
    allowed_domains = ['www.huffpost.com']
    start_urls = ['https://www.huffpost.com/']

    def start_requests(self):
        return [scrapy.Request(self.start_urls[0],
                               callback=self.parse,
                               headers=headers)]

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find(re.compile(r'h1|p'), attrs={'class': re.compile(r'headline')}).text.strip()

            byline = soup.find('div', attrs={'class': re.compile(r'byline')})
            item['byline'] = byline.text.strip() if byline else None

            date = soup.find('div', attrs={'class':'timestamp'})\
                .span.text.strip().replace('ET', 'EDT')
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', {'class': re.compile('entry__content')})
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')
            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile(r'/entry/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse, headers=headers)
