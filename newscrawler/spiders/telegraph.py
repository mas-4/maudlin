import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class TelegraphSpider(scrapy.Spider, BoilerPlateParser):
    name = 'telegraph'
    allowed_domains = ['www.telegraph.co.uk']
    start_urls = ['https://www.telegraph.co.uk/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', {'itemprop': re.compile(r'headline')}).text.strip()

            if byline := soup.find('span', attrs={'data-test': 'author-name'}):
                item['byline'] = byline['content']
            elif byline := soup.find('div', class_='byline'):
                item['byline'] = byline.text.strip()
            else:
                item['byline'] = None

            date = soup.find('time')['datetime']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', attrs={'data-test': 'article-body-text'})
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            href = re.compile('/\d{4}/\d{2}/\d{2}/')
            links = set(a['href'] for a in soup.find_all('a', attrs={'href': href}))
            for link in links:
                yield response.follow(link, callback=self.parse)
