import re, requests
from bs4 import BeautifulSoup

def get_text(url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for header in soup.find_all(re.compile('^h[1-6]$')):
        if (header.text).lower() in ["ingredients","ingredients:"]:
            print('-------------------------------------')
            ingredients = header.parent
            for bullet in ingredients.findAll('li'):
                print(bullet.text)

urls = ['https://damndelicious.net/2014/12/13/pasta-sun-dried-tomato-cream-sauce/',
        'https://www.recipetineats.com/chicken-with-creamy-sun-dried-tomato-sauce/',
       ]

for url in urls:
    get_text(url)