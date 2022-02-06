from django.shortcuts import render

import re, requests
from bs4 import BeautifulSoup

ingredient_header = ['ingredients', 'ingredients:']
instructions_header = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:']
testing_urls = ['https://damndelicious.net/2014/12/13/pasta-sun-dried-tomato-cream-sauce/',
                'https://www.recipetineats.com/chicken-with-creamy-sun-dried-tomato-sauce/',
                'https://www.livewellbakeoften.com/soft-and-chewy-chocolate-chip-cookies-recipe/',
]

def get_text(soup):
    title = soup.find('h1').text
    for header in soup.find_all(re.compile('^h[1-6]$')):
        header_text = (header.text).lower()
        if header_text in ingredient_header:
            # ingredient =  re.compile('[A-Za-z0-9 _.,!"'/$]*')
            # re.sub(r'[^\x00-\x7f]',r'', ingredient.text)
            ingredients = [re.sub(r'[^\x00-\x7f]',r'', ingredient.text) for ingredient in header.parent.findAll('li')]
        elif header_text in instructions_header:
            instructions = [instruction.text for instruction in header.parent.findAll('li')]
    return {'ingredients': ingredients, 'instructions': instructions, 'title': title}
    
def simplify_recipe(request):
    recipe_data = {}
    if request.method == 'POST':
        url = request.POST['url']
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser') 
        recipe_data = get_text(soup)
    return render(request, 'simplifyRecipe/recipe_temp.html', recipe_data)