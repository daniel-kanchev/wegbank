import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from wegbank.items import Article


class WegbankSpider(scrapy.Spider):
    name = 'wegbank'
    start_urls = ['https://weg-bank.de/de/weg-bank-news']
    page = 1


    def parse(self, response):
        articles = response.xpath('//div[@class="article-list"]/div')
        if articles:
            for article in articles:
                link = article.xpath('.//a[@class="button button--link     "]/@href').get()
                date = article.xpath('./p[@class="article-list__item-date"]/text()').get()
                if date:
                    date = date.strip()

                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

            self.page += 1
            next_page = f'https://weg-bank.de/de/weg-bank-news?page={self.page}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//title/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="column-text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
