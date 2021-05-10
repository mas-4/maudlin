from newscrawler.items import NewscrawlerItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import signals

class BoilerPlateParser:
    def prepopulate_item(self, response):
        item = NewscrawlerItem()
        item['agency'] = self.name
        item['start'] = self.start_urls[0]
        item['url'] = response.url
        return item

    def joinparagraphs(self, paragraphs):
        text = []
        for p in paragraphs:
            text.append(p.text.strip())
        text = list(filter(lambda l: l.strip(), text))
        return '\n\n'.join(text).replace('\xa0', ' ')


class SeleniumMixin:
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def spider_closed(self):
        self.driver.close()
