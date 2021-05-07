import scrapy


class NewscrawlerItem(scrapy.Item):
    start = scrapy.Field()
    agency = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    byline = scrapy.Field()
    text = scrapy.Field()
