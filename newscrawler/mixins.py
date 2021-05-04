from newscrawler.items import NewscrawlerItem

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
        return '\n\n'.join(text)

