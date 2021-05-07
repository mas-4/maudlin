import re
import scrapy
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class UsaSpider(scrapy.Spider, BoilerPlateParser):
    name = 'usa'
    allowed_domains = ['www.usatoday.com']
    start_urls = ['https://www.usatoday.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0] and 'videos' not in response.url:
            item = self.prepopulate_item(response)

            title = soup.find('h1', class_='gnt_ar_hl')
            if not title:
                title = soup.find('h1', class_='topper__headline')
            item['title'] = title.text.strip()

            byline = soup.find(attrs={'class': re.compile('gnt_ar_by')})
            if not byline:
                byline = soup.find(attrs={'class': re.compile('topper__byline')})
            item['byline'] = byline.text.strip()

            date = soup.find('time')
            if date:
                date = date.text.strip()
                date = parser.parse(date)
            else:
                date = soup.find('div', class_='gnt_ar_dt')['aria-label']
                date = date.split('Updated')[0]
                date = date.strip('Published: ')
                date = parser.parse(date)
            item['date'] = date

            story = soup.find('div', class_='gnt_ar_b')
            if not story:
                story = soup.find('section', class_='in-depth-content')
            paragraphs = story.find_all('p')
            text = self.joinparagraphs(paragraphs)
            item['text'] = text.replace('\xa0', ' ')

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('main', class_='gnt_cw')
            links = root.find_all('a')
            for link in links:
                try:
                    yield response.follow(link['href'], callback=self.parse)
                except:
                    continue
