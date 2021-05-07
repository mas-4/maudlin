import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class AbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'abc'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['https://abcnews.go.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', class_='Article__Headline__Title').text.strip()
            item['byline'] = soup.find('span', class_='Byline__Author').text.strip()

            date = soup.find('div', class_='Byline__Meta Byline__Meta--publishDate').text.strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('section', class_='Article__Content story')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('section', id='main-container')
            links = root.find_all('a', class_='black-ln')
            for link in links:
                yield response.follow(link['href'], callback=self.parse)
