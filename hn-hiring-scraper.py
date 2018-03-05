from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from kinto_http import Client

# specify the url
quote_page = Request("file:///source/data.html")

# query the website and return the html to the variable 'page'
page = urlopen(quote_page)

# parse the html using beautiful soap and store in variable `soup`
soup = BeautifulSoup(page, 'html.parser')

# Take the row of the comments
offers = soup.findAll('tr', attrs={'class': 'athing'})
#kinto client
client = Client(server_url="https://kinto-instance-sample.herokuapp.com/v1/"
                , auth=('mozilla-username', 'mozilla-password'))

info = client.server_info()
assert 'schema' in info['capabilities'], "Server doesn't support schema validation."

# To get an existing bucket
bucket_id = 'hn'
try:
    bucket = client.get_bucket(id=bucket_id)
except:
    # To create a bucket.
    client.create_bucket(id=bucket_id)


# Or get an existing one.
collection_id = 'hn-hiring'
try:
    collection = client.get_collection(id=collection_id, bucket=bucket_id)
except:
    # To create a bucket.
    client.create_collection(id=collection_id, bucket=bucket_id)

for o in offers:
    comm_id = o.get('id')
    a = o.find('span', attrs={'class': 'c00'})
    if a:
        text = a.text.strip()
        if '|' in text:
            client.update_record(data={'text': text}, id=comm_id
                                 , collection=collection_id, bucket=bucket_id)
