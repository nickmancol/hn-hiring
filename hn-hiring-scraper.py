from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv

# specify the url
src_pages = ['16052538', '16492994', '16282819' ]

def extract_header(text=''):
    header = '|'.join(p[0:min(50, len(p))] for p in text.replace('\n', ' ').split('|'))
    return header

def extract_opps(src_pages=[], local=False):
    opps = [('article_id', 'header', 'text')]
    src_pages.sort(reverse=True)

    for pageid in src_pages:
        src_page = pageid
        if not local:
            src_page = 'https://news.ycombinator.com/item?id='+pageid
        # query the website and return the html to the variable 'page'
        page = urlopen(src_page)

        # parse the html using beautiful soap and store in variable `soup`
        soup = BeautifulSoup(page, 'html.parser')

        # Take the row of the comments
        offers = soup.findAll('tr', attrs={'class': 'athing'})
        for o in offers:
            comm_id = o.get('id')
            a = o.find('span', attrs={'class': 'c00'})
            if a:
                text = a.text.strip().replace('\nreply','')
                #TODO: change this selection criteria
                if '|' in text:
                    header = extract_header(text)
                    opps.append((comm_id, header, text))

    return opps


def serialize(filename, opps=[]):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(opps)

if __name__ != "main":
    serialize('data.csv', extract_opps(
        ['file:///home/nickman/code/hn-hiring/data/1-2018.html'
        ,'file:///home/nickman/code/hn-hiring/data/2-2018.html'
        ,'file:///home/nickman/code/hn-hiring/data/3-2018.html']
            , local=True))
