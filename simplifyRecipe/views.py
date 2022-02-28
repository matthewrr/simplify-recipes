from django.shortcuts import render

import os, json, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

url_dict = {}
ingredient_label = ['Ingredients', 'Ingredients:', 'ingredients', 'ingredients:']
instruction_label = ['instructions', 'instructions:', 'steps', 'steps:', 'directions', 'directions:',
    'Instructions', 'Instructions:', 'Steps', 'Steps:', 'Directions', 'Directions:']
#use regex

def log_url(url_dict):
    with open(os.path.abspath(os.getcwd()) + '/simplifyRecipe/static/json/websites.json', 'r+') as file:
        file_data = json.load(file)

        #check if alredy logged
        base_url = list(url_dict.keys())[0]
        website_list = file_data['websites']
        all_websites = []
        for item in website_list:
            all_websites.append(list(item)[0])

        if base_url in all_websites:
            return

        #log base URL if new to JSON file
        file_data['websites'].append(url_dict)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
    return

def combine(child_objs, header_label):
    result = []
    for obj in child_objs:
        content = obj.findAll(text=True)
        foo = ' '.join([item.strip() for item in content if item.strip()])
        result.append(foo)
    if result: url_dict[header_label]['combine'] = True
    return ' '.join(result)

def simple_tags(section, header_label, tag):
    result = []
    pattern = re.compile(r'[^\x11-\x7f\u00BC-\u00BE]')
    try:
        result = [item.text for item in section.findAll(tag)]
    except:
        pass
    if result:
        url_dict[header_label]['tags'] = {
            'single': True,
            'tag_label': tag
        }
        return result
    return result

def nested_tags(section, header_label):
    result = []
    tags = {'ul':'li','ol':'li','tr':'td'}
    for parent, child in tags.items():
        parent_objs = []
        try: parent_objs = section.findAll(parent)
        except: continue
        for parent_obj in parent_objs:
            child_objs = parent_obj.findAll(child)
            content = [item.text for item in child_objs]
            if parent == 'tr':
                result.append(combine(child_objs, header_label, section))
            elif content: 
                result += content
                url_dict[header_label]['tags'] = {
                    'single': False,
                    'tag_label': {parent:child}
                }
    #try single tags
    if not result:
        for tag in ['p']: #leave room open for additional tags
            result = simple_tags(section, header_label, tag)
            if result: return result
    return result

def get_data(section, header_label):
    result = []
    for i in range(4):
        result = nested_tags(section, header_label)
        if result:
            url_dict[header_label]['parent_height'] = i
            return result
        section = section.parent #best practice to use else?
    return result

def get_recipe(soup, url):
    base_url = urlparse(url).hostname
    page_title = soup.find('h1').text
    #check if page_title exists
    
    keys = ['parent_height', 'tags', 'combine']
    url_dict.update({
        'ingredients': dict.fromkeys(keys),
        'instructions': dict.fromkeys(keys)
    })
    lst = soup.find_all(re.compile('^h[2-6]$'))
    for i in lst:
        if (i.text).strip() in instruction_label:
            instructions_header = i
        elif (i.text).strip() in ingredient_label:
            ingredients_header = i
    ingredients = get_data(ingredients_header, 'ingredients')
    instructions = get_data(instructions_header, 'instructions')
    context = {
        'base_url': base_url,
        'title': page_title,
        'ingredients': ingredients,
        'instructions': instructions,
    }
    log_url({base_url: url_dict})
    return context

def simplify_recipe(request):
    context = {'valid_url': True, 'extraction': True, 'modal': False}
    if request.method == 'POST':
        url = request.POST['url']
        context['url'] = url
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser') 
            context = get_recipe(soup, url)
            context.update(url=True,valid_url=True,extraction=True)
        except UnboundLocalError as err:
            context['modal'] = 'failed_extraction'
        except requests.exceptions.MissingSchema as err:
            context['modal'] = 'invalid_url'

    return render(request, 'simplifyRecipe/recipe_card.html', context)