import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


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
            item['byline'] = byline.text.strip() if byline else None

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
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            href = re.compile('/\d{4}/\d{2}/\d{2}/')
            links = set(a['href'] for a in soup.find_all('a', attrs={'href': href}))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                if '/restricted/' in link:
                    continue
                if 'picture-gallery' not in link:
                    yield response.follow(link, callback=self.parse)
