import re, requests
from bs4 import BeautifulSoup

ingredient_header = ['ingredients', 'ingredients:']
instructions_header = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:']
url = 'https://damndelicious.net/2014/12/13/pasta-sun-dried-tomato-cream-sauce/'

def get_text(soup):
    for header in soup.find_all(re.compile('^h[1-6]$')):
        header_text = (header.text).lower()
        if header_text in ingredient_header:
            ingredients = [ingredient.text for ingredient in header.parent.findAll('li')]
        elif header_text in instructions_header:
            instructions = [instruction.text for instruction in header.parent.findAll('li')]
    return [instructions, ingredients]

def simplify_recipe(url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser') 
    instructions, ingredients = get_text(soup)

simplify_recipe(url)

# urls = ['https://damndelicious.net/2014/12/13/pasta-sun-dried-tomato-cream-sauce/',
    #     'https://www.recipetineats.com/chicken-with-creamy-sun-dried-tomato-sauce/',
    #    ]