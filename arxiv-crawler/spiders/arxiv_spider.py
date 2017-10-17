import scrapy

class ArxivSpider(scrapy.Spider):
    """ArxivSpider class which scans arxiv listings and checks authors on inspire"""
    name = "arxiv"

    def __init__(self, filename=None):
        # get the listings, either from file if defined or by default
        # use hep-ph, hep-th
        if filename:
            with open(filename, 'r') as f:
                self.listings = [l.rstrip('\n') for l in f.readlines()]
        else:
            self.listings = ['hep-ph','hep-th']

    def start_requests(self):
        # set urls from listings
        urls = ['https://arxiv.org/list/'+lst+'/new' for lst in self.listings]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_data(self, response):
        # get the actual data from the arxiv website and save as dict
        for quote in response.css('div.meta'):
            if (len(quote.css('p.mathjax::text').extract())>0):
                yield {
                    'title': quote.css('div.list-title::text').extract()[-1][1:].replace('\n',''),
                    'authors': quote.css('div.list-authors a::text').extract(),
                    'abstract': quote.css('p.mathjax::text').extract()[-1],
                    'subject': quote.css('span.primary-subject::text').extract()[-1],
                }
                
    def parse(self, response):
        # loop over each article found on arxiv
        for val in self.get_data(response):
            # get the author list in inspire-parseable format
            auths='f+a+'
            for auth in val['authors']:
                auths+=auth+'+or+a+'
            auths=auths[:-6] # remove the last +or+f+a+
            url = 'http://inspirehep.net/search?ln=en&ln=en&p='+auths+'&rm=citation&rg=25'
            # look up the authors on inspirehep
            yield scrapy.Request(url=url,
                                 meta={'authors' : val['authors'],
                                       'title' : val['title'],
                                       'abstract' : val['abstract'],
                                       'subject' : val['subject']},
                                 callback=self.parseAuthors)


    def get_score(self, response):
        # assign score to article based on total citation count of top
        # 25 papers by all authors
        score=0
        for quote in response.css('div.rankscoreinfo'):
            val = quote.css('a::text').extract()[0][1:-1]
            score+=int(val)
        return score
        
    def parseAuthors(self, response):
        # get a score and all the info to a dict
        current_score = self.get_score(response)
        filename = 'scored-arxiv'
        yield {
            'score' : current_score,
            'authors' : response.meta['authors'],
            'abstract' : response.meta['abstract'],
            'title' : response.meta['title'],
            'subject' : response.meta['subject']
        }
