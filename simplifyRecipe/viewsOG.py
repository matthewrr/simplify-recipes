from colorsys import TWO_THIRD
from django.shortcuts import render

import re, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ingredient_header = ['ingredients', 'ingredients:']
instructions_header = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:']
url_list = [
    'https://www.averiecooks.com/garlic-butter-chicken/',
    'https://recipeland.com/recipe/v/bhg-fudge-brownies-50409',
    'https://www.southernliving.com/recipes/slow-cooker-french-onion-soup',
    'https://www.allrecipes.com/recipe/81568/afghan-beef-raviolis-mantwo/',
    'https://food52.com/recipes/87369-best-cajun-chicken-and-rice-recipe', #double sections
    'https://www.foodnetwork.com/recipes/ree-drummond/cinnamon-baked-french-toast-recipe-2120484',
    'https://www.yummly.com/recipe/Black-Bean-Chili-9093664',

]
#double sections --> see food52
#foodnetwork (had to parent up... works now)
#yummly... only li, no ol/ul. requires captcha
#epicurious requires login
#https://recipeland.com/recipe/v/bhg-fudge-brownies-50409 table, paragraphs, metric issue

# reasons = ['captcha', 'login', 'invalid_url', 'other']
# d = {'example.com': 'reason'}
# regularly audit both full pulls for popular websites and simple len of items to see if website design changed.

pattern = re.compile(r'[^\x11-\x7f\u00BC-\u00BE]')

def update_websites(base_url):
    pass


def simple_tags(section):
    result = []
    tags = ['p','li']
    for tag in tags:
        items = section.findAll(tag)
        for item in items:
            result.append(re.sub(pattern, r'', item.text))
    return result


def nested_tags(section, source, label, d):
    depth = 0
    result = []
    tags = {'ul':'li','ol':'li','tr':'td'}
    for parent, child in tags.items():
        parent_objs = section.findAll(parent)
        for parent_obj in parent_objs:
            depth +=1
            child_objs = parent_obj.findAll(child)
            content = [item.text for item in child_objs]
            if content: result.append(' '.join(content))
            else: #loop deeper
                depth += 1
                for obj in child_objs:
                    content = obj.findAll(text=True)
                    foo = ' '.join([item.strip() for item in content if item.strip()])
                    result.append(foo)
    d[source][label] = {
        'outer': parent,
        'inner': child,
        'depth': depth
        }
    return result

def get_data(section, source, label, d):
    result = []
    for i in range(4):
        result = nested_tags(section, source, label, d)
        result = simple_tags(section)
        if result:
            d[source][label]['height'] = i
        else:
            section = section.parent
    return result

def get_recipe(soup, url):
    source = urlparse(url).hostname
    d = {}
    d[source] = {}
    title = soup.find('h1').text
    for header in soup.find_all(re.compile('^h[1-6]$')):
        header_text = (header.text.lower()).strip()
        section = header.parent
        if header_text in ingredient_header:
            ingredients = get_data(section, source, 'ingredients', d)
        elif header_text in instructions_header:
            instructions = get_data(section, source, 'instructions', d)
    print(d)
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