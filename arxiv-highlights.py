#!/usr/bin/env python3
"""Python script to scan arxiv papers and create a list of highlights
based on author citation counts.
Usage:
 ./arxiv-scan.py [-n ntop] [-o filename] [-a listings]
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import contextlib, os, json, sys, argparse

parser = argparse.ArgumentParser(description='Scrape data from arxiv and create top list of daily papers')

parser.add_argument('-o',action='store',default='arxiv.json',dest='filename')
parser.add_argument('-a',action='store',default=None,dest='listings')
parser.add_argument('-n',action='store',type=int,default=8,dest='ntop')

args=parser.parse_args()

# remove json if already there
with contextlib.suppress(FileNotFoundError):
    os.remove(args.filename)
    
# get settings
settings = get_project_settings()
# write out to json
settings.set('FEED_FORMAT', 'json')
settings.set('FEED_URI', args.filename)
# create the crawler process
process = CrawlerProcess(settings)


# start the 'arxiv' spider.
process.crawl('arxiv', filename=args.listings)
process.start() # the script will block here until the crawling is finished

with open(args.filename) as data_file:    
    data = json.load(data_file)


first=True
print('\n# Starting ranked list of today\'s top '+str(args.ntop)+' on arxiv\n')
sorted_data = sorted(data, key=lambda k: k['score'])

# loop over the first ntop best scored values
for val in sorted_data[:-args.ntop:-1]:
    if (first):
        first=False
    else:
        print('====================\n')
    print("'"+val['title']+"'",'('+str(val['score'])+')')
    auths = ''
    for a in val['authors']:
        auths+=a+', '
    auths = auths[:-2]
    print('  - by',auths,'\n',val['subject'],'\n')
    print(val['abstract'])
