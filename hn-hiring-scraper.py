from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv

# specify the url
src_pages = ['16052538', '16492994', '16282819' ]


class HNOpp(object):
    #just to use a set as a way to avoid duplicates, __eq__ and __hash__ are nonsense
    def __init__(self, id, header, text):
        self.id = id
        self.header = header
        self.text = text

    def __eq__(self, other):
        return self.text.lower() == other.text.lower()

    def __hash__(self):
        return hash(self.text.lower())

    def as_tuple(self):
        return (self.id, self.header, self.text)


def extract_opps(src_pages=[], local=False):
    opps = set([])
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
                header = ' '.join(a.findAll(text=True, recursive=False)).strip()
                #TODO: change this selection criteria
                if '|' in header:
                    text = '\n '.join([p.text.strip() for p in a.find_all('p')])
                    opps.add(HNOpp(comm_id, header, text))

    return opps


def serialize(filename, opps=[]):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['article_id', 'header', 'text'])
        writer.writerows([o.as_tuple() for o in opps])

if __name__ != "main":
    serialize('data.csv', extract_opps(src_pages, local=False))
