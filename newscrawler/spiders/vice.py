from newscrawler.models import Article
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class ViceSpider(scrapy.Spider, BoilerPlateParser):
    name = 'vice'
    allowed_domains = ['www.vice.com']
    start_urls = ['https://www.vice.com/en']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='smart-header__hed').text.strip()
            item['byline'] = soup.find('div', class_='contributor__meta').a.text.strip()

            date = soup.find(
                'div',
                class_='article__header__datebar__date--original').text.strip()
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='article__body-components')
            paragraphs = article.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text
            yield item

        if response.url == self.start_urls[0]:
            attrs={'class': 'vice-card-hed__link'}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
