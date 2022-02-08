from django.shortcuts import render

import re, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ingredient_header = ['ingredients', 'ingredients:']
instructions_header = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:']

def get_text(soup, url):
    source = urlparse(url).hostname
    title = soup.find('h1').text
    for header in soup.find_all(re.compile('^h[1-6]$')):
        header_text = header.text.lower()
        if header_text in ingredient_header:
            ingredients = [re.sub(r'[^\x00-\x7f]',r'', ingredient.text) for ingredient in header.parent.findAll('li')]
        elif header_text in instructions_header:
            instructions = [instruction.text for instruction in header.parent.findAll('li')]
    return {'ingredients': ingredients, 'instructions': instructions, 'source': source, 'title': title, 'url': url, 'valid_url': True, 'extraction': True}

def simplify_recipe(request):
    recipe_data = {'valid_url': False, 'extraction': False, 'modal': False}
    if request.method == 'POST':
        url = request.POST['url']
        recipe_data['url'] = url
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser') 
            recipe_data = get_text(soup, url)
        except UnboundLocalError as err:
            recipe_data['valid_url'] = True
            recipe_data['modal'] = 'failed_extraction'
        except requests.exceptions.MissingSchema as err:
            recipe_data['modal'] = 'invalid_url'
    return render(request, 'simplifyRecipe/recipe_temp.html', recipe_data)