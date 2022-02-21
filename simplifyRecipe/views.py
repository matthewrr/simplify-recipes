from django.shortcuts import render

import re, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ingredient_header = ['ingredients', 'ingredients:']
instructions_header = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:']

def extract_data(header):
    pattern = re.compile(r'[^\x11-\x7f\u00BC-\u00BE]') #standard ascii minus first 11 (10 is newline) plus fractions
    unnested = ['p']
    nested_single = {'tr':'td'}
    nested_multiple = {'ul':'li','ol':'li','tr':'td'}
    result = []

    for tag in unnested:
        items = header.findAll(tag)
        for item in items:
            result.append(re.sub(pattern, r'', item.text))
        if result: return result
    for k, v in nested_single.items():
        parent_items = header.findAll(k) 
        for item in parent_items:
            child_items = item.findAll(v) #combine with finding text
            l = [child.text for child in child_items]
            result.append(' '.join(l))
        if len(result) > 1:
            return result
        else:
            result.clear()
    for k, v in nested_multiple.items():
        parent_items = header.findAll(k)
        for item in parent_items:
            child_items = item.findAll(v)
            for child_item in child_items:
                find_text = child_item.findAll(text=True)
                temp = []
                for item in find_text:
                    stripped = item.strip()
                    if stripped:
                        temp.append(stripped)
                ' '.join(temp)
                result.append(' '.join(temp))
        if result: return result
    return result

def get_recipe(soup, url):
    source = urlparse(url).hostname
    title = soup.find('h1').text
    for header in soup.find_all(re.compile('^h[1-6]$')):
        header_text = (header.text.lower()).strip()
        if header_text in ingredient_header:
            ingredients = extract_data(header.parent)
            if not ingredients: ingredients = extract_data(header.parent.parent)
        elif header_text in instructions_header:
            instructions = extract_data(header.parent)
            if not instructions: extract_data(header.parent.parent)
    return {'ingredients': ingredients, 'instructions': instructions, 'source': source, 'title': title, 'url': url, 'valid_url': True, 'extraction': True}

def simplify_recipe(request):
    recipe_data = {'valid_url': False, 'extraction': False, 'modal': False}
    if request.method == 'POST':
        url = request.POST['url']
        recipe_data['url'] = url
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser') 
            recipe_data = get_recipe(soup, url)
        except UnboundLocalError as err:
            recipe_data['valid_url'] = True
            recipe_data['modal'] = 'failed_extraction'
        except requests.exceptions.MissingSchema as err:
            recipe_data['modal'] = 'invalid_url'
    return render(request, 'simplifyRecipe/recipe_card.html', recipe_data)

#list sites that require sign-in
#error out if no bullets
#https://recipeland.com/recipe/v/bhg-fudge-brownies-50409 table, paragraphs, metric issue