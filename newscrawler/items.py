# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    url = scrapy.field()
    title = scrapy.field()
    date = scrapy.field()
    byline = scrapy.field()
    text = scrapy.field()
