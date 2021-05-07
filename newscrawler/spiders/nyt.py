import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class NytSpider(scrapy.Spider, BoilerPlateParser):
    name = 'nyt'
    allowed_domains = ['www.nytimes.com']
    start_urls = ['https://www.nytimes.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find('h1', attrs={'data-test-id': 'headline'}).text.strip()
            item['byline'] = soup.find('span', class_='last-byline').text.strip()

            date = soup.find('time')['datetime'].strip()
            date = parser.parse(date)
            item['date'] = date

            story = soup.find('section', attrs={'name': 'articleBody'})
            if not story:
                story = soup.find('article', class_='live-blog-content')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            links = set([a['href'] for a in soup.find_all('a', attrs={'data-story': True})])

            for link in links:
                yield response.follow(link, callback=self.parse)
