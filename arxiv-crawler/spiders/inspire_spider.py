

import scrapy


class ArxivSpider(scrapy.Spider):
    name = "arxiv"

    def start_requests(self):
        urls = [
            'https://arxiv.org/list/hep-ph/new',
            'https://arxiv.org/list/hep-th/new',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div.meta'):
            if (len(quote.css('p.mathjax::text').extract())>0):
                yield {
                    'title': quote.css('div.list-title::text').extract()[-1].replace('\n',''),
                    'authors': quote.css('div.list-authors a::text').extract(),
                    'abstract': quote.css('p.mathjax::text').extract()[-1],
                    'subjet': quote.css('span.primary-subject::text').extract()[-1],
                }
        # page = response.url.split("/")[-2]
        # filename = 'arxiv-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write()
        #     # f.write(response.body)
        # self.log('Saved file %s' % filename)

