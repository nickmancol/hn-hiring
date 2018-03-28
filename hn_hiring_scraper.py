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

def serialize_filters(filename, opps=[]):
    schema = Schema(id=ID(stored=True), header=TEXT, text=TEXT)
    ix = create_in("./", schema)
    writer = ix.writer()
    res = {}
    for o in opps:
        writer.add_document(id=o.id, header=o.header, text=o.text)
        res[o.id] = {'opp':o,'languages': [], 'cities': [], 'roles': [], 'perks': []}

    writer.commit()
    set_tags(ix, res, 'cities', 'header', './cities.csv')
    set_tags(ix, res, 'perks', 'header', './perks.csv')
    set_tags(ix, res, 'languages', 'text', './languages.csv')
    set_tags(ix, res, 'roles', 'text', './roles.csv')
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['article_id','header','text']
                        +['city_'+str(i) for i in range(1,4)]
                        +['lang_'+str(i) for i in range(1,4)]
                        +['role_'+str(i) for i in range(1,4)]
                        +['perk_'+str(i) for i in range(1,4)])
        for k in res.keys():
            curr = res[k]
            row = []
            row += curr['opp'].as_tuple()
            row += get_list_vals(curr, 'cities')
            row += get_list_vals(curr, 'languages')
            row += get_list_vals(curr, 'roles')
            row += get_list_vals(curr, 'perks')
            writer.writerow(row)


def get_list_vals(row, field, max=3):
    res = []
    for i in range(0, max):
        val = None
        if i < len(row[field]):
            val = str(row[field][i]).strip()
        res.append(val)
    return res


def set_tags(index, opps_dict, dict_key, search_field, filesrc):
    with index.searcher() as searcher:
        parser = QueryParser(search_field, index.schema)
        with open(filesrc) as f:
            cities = f.readlines()
        for c in cities:
            querystr = And([Term(search_field, token.lower()) for token in c.strip().split(' ')])
            results = searcher.search(querystr, limit=None)
            for r in results:
                opps_dict[r['id']][dict_key].append(c)



if __name__ != "main":
    opps = extract_opps(src_pages, local=False)
    serialize_filters("filters.csv", opps)
