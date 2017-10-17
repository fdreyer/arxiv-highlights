

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

    def get_data(self, response):
        for quote in response.css('div.meta'):
            if (len(quote.css('p.mathjax::text').extract())>0):
                yield {
                    'title': quote.css('div.list-title::text').extract()[-1][1:].replace('\n',''),
                    'authors': quote.css('div.list-authors a::text').extract(),
                    'abstract': quote.css('p.mathjax::text').extract()[-1],
                    'subject': quote.css('span.primary-subject::text').extract()[-1],
                }
                
    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'arxiv-%s.html' % page
        
        for val in self.get_data(response):
            auths='f+a+'
            for auth in val['authors']:
                auths+=auth+'+or+a+'
            auths=auths[:-6] # remove the last +or+f+a+
            url = 'http://inspirehep.net/search?ln=en&ln=en&p='+auths+'&rm=citation&rg=25'
            yield scrapy.Request(url=url,
                                 meta={'authors' : val['authors'],
                                       'title' : val['title'],
                                       'abstract' : val['abstract'],
                                       'subject' : val['subject']},
                                 callback=self.parseAuthors)


    def get_score(self, response):
        score=0
        for quote in response.css('div.rankscoreinfo'):
            val = quote.css('a::text').extract()[0][1:-1]
            score+=int(val)
        return score
        
    def parseAuthors(self, response):
        current_score = self.get_score(response)
        filename = 'scored-arxiv'
        yield {
            'score' : current_score,
            'authors' : response.meta['authors'],
            'abstract' : response.meta['abstract'],
            'title' : response.meta['title'],
            'subject' : response.meta['subject']
        }
