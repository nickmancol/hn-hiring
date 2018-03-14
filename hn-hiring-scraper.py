from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json

# specify the url
src_pages = ['16492994', '16282819', '16052538']

def extract_header(text=''):
    header = '|'.join(p[0:min(50, len(p))] for p in text.replace('\n', ' ').split('|'))
    return header

def extract_opps(src_pages=[]):
    opps = []
    for pageid in src_pages:
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
                text = a.text.strip()
                #TODO: change this selection criteria
                if '|' in text:
                    header = extract_header(text)
                    opps.append({'id': comm_id, 'text': text, 'header': header})

    return opps


def serialize(filename, opps=[]):
    with open(filename, 'w') as outfile:
        json.dump(opps, outfile)

if __name__ != "main":
    serialize('data.json', extract_opps(src_pages))
