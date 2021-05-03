# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    start = scrapy.Field()
    agency = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    byline = scrapy.Field()
    text = scrapy.Field()
