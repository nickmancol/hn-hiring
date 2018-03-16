from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
import csv

# specify the url
src_pages = ['16052538', '16492994', '16282819' ]
suspects = []

class HNOpp(object):
    #just to use a set as a way to avoid duplicates, __eq__ and __hash__ are nonsense
    def __init__(self, id, header, text, tags=[]):
        self.id = id
        self.header = header
        self.text = text
        self.tags = tags

    def __eq__(self, other):
        return self.text.lower() == other.text.lower()

    def __hash__(self):
        return hash(self.text.lower())

    def as_tuple(self):
        return (self.id, self.header, self.text)


def extract_header(text=''):
    header = '|'.join(p[0:min(50, len(p))] for p in text.replace('\n', ' ').split('|'))
    return header


def extract_text(html_tag):
    text = ''
    for x in html_tag.findAll('p'):
        if len(x.contents) > 0:
            first_content = str(x.contents[0])
            if not first_content.startswith('<font'):
                text += ' '+first_content.strip()

    return text.replace('\nreply', '')


def extract_opps(src_pages=[], local=False):
    opps = set([])
    src_pages.sort(reverse=True)

    for pageid in src_pages:
        src_page = pageid
        if not local:
            src_page = 'https://news.ycombinator.com/item?id='+pageid
        page = urlopen(src_page)
        soup = BeautifulSoup(page, 'html.parser')

        # Take the row of the comments
        offers = soup.findAll('tr', attrs={'class': 'athing'})
        for o in offers:
            comm_id = o.get('id')
            a = o.find('span', attrs={'class': 'c00'})
            if a:
                header = ' '.join(a.findAll(text=True, recursive=False)).strip()
                #TODO: change this selection criteria
                if '|' in header:
                    text = extract_text(a)
                    opps.add(HNOpp(comm_id, extract_header(header), text))

    return opps


def serialize(filename, opps=[]):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['article_id', 'header', 'text'])
        writer.writerows([o.as_tuple() for o in opps])


def serialize_filters(filename, opps=[]):
    schema = Schema(id=ID, header=TEXT, text=TEXT)
    ix = create_in("./", schema)
    writer = ix.writer()
    res = {}
    for o in opps:
        writer.add_document(id=o.id, header=o.header, text=o.text)
        res[o.id] = {'languages': [], 'cities': [], 'roles': []}

    writer.commit()
    set_cities(ix, res)

def set_cities(index, opps_dict):
    with index.searcher() as searcher:
        parser = QueryParser("header", index.schema)
        with open('./cities.csv') as f:
            cities = f.readlines()
        for c in cities:
            querystr = And([Term("header", token) for token in c.strip().split(' ')])
            results = searcher.search(querystr)
            if len(results) > 0:
                print(results)

if __name__ != "main":
    opps = extract_opps([
            'file:///home/nickman/code/hn-hiring/data/1-2018.html'
            #,'file:///home/nickman/code/hn-hiring/data/2-2018.html'
            #,'file:///home/nickman/code/hn-hiring/data/3-2018.html'
    ], local=True)
    serialize_filters("filters.csv", opps)
    #serialize('data.csv', opps)
