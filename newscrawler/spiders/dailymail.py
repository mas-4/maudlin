from newscrawler.models import Article
import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser, SeleniumMixin

class DailymailSpider(scrapy.Spider, BoilerPlateParser, SeleniumMixin):
    name = 'dailymail'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    allowed_domains = ['www.dailymail.co.uk']
    start_urls = ['https://www.dailymail.co.uk/ushome/index.html']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
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
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
