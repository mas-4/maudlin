from newscrawler.models import Article
import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class BlazeSpider(scrapy.Spider, BoilerPlateParser):
    name = 'blaze'
    allowed_domains = ['theblaze.com']
    start_urls = ['https://www.theblaze.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='headline').text.strip()
            item['byline'] = soup.find(
                'a', class_='post-author__name').text.strip()

            date = soup.find('span', class_='post-date').text.strip()
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='body-description')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile(r'https://www.theblaze.com/news/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
