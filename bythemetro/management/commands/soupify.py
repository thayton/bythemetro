import re
import string

from unescape import unescape
from BeautifulSoup import BeautifulSoup, Comment, Tag

def soupify(page):
    s = BeautifulSoup(page)

    # Remove unwanted tags
    tags = s.findAll(lambda tag: tag.name == 'script' or \
                                 tag.name == 'style')
    for t in tags:
        t.extract()
        
    # Remove comments
    comments = s.findAll(text=lambda text:isinstance(text, Comment))
    for c in comments:
        c.extract()

    # Remove entity references?
    return s

def get_all_text(s):
    t = s.findAll(text=True)
    t = unescape(' '.join(t))
    t = ' '.join(t.split())
    return t

def get_mailto(s):
    if isinstance(s, unicode):
        m = re.search(r'[\S]+@[\S]+\w', s)
        if m:
            return m.group(0)
    elif isinstance(s, Tag):
        if s.has_key('href'):
            return s['href'].startswith('mailto:') and s['href'][7:] or s['href']
        else: 
            a = s.find('a', href=re.compile(r'^mailto:'))
            if a:
                return a['href'].startswith('mailto:') and a['href'][7:] or a['href']

    return None

# From https://gist.github.com/104413
def extract_form_fields(soup):
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll('input'):
        # ignore submit/image with no name attribute
        if input['type'] in ('submit', 'image') and not input.has_key('name'):
            continue
        
        # single element nome/value fields
        if input['type'] in ('text', 'hidden', 'password', 'submit', 'image'):
            value = ''
            if input.has_key('value'):
                value = input['value']
            fields[input['name']] = value
            continue
        
        # checkboxes and radios
        if input['type'] in ('checkbox', 'radio'):
            value = ''
            if input.has_key('checked'):
                if input.has_key('value'):
                    value = input['value']
                else:
                    value = 'on'
            if fields.has_key(input['name']) and value:
                fields[input['name']] = value
            
            if not fields.has_key(input['name']):
                fields[input['name']] = value
            
            continue
        
#        assert False, 'input type %s not supported' % input['type']
    
    # textareas
    for textarea in soup.findAll('textarea'):
        fields[textarea['name']] = textarea.string or ''
    
    # select fields
    for select in soup.findAll('select'):
        value = ''
        options = select.findAll('option')
        is_multiple = select.has_key('multiple')
        selected_options = [
            option for option in options
            if option.has_key('selected')
        ]
        
        # If no select options, go with the first one
        if not selected_options and options:
            selected_options = [options[0]]
        
        if not is_multiple:
            assert(len(selected_options) < 2)
            if len(selected_options) == 1:
                value = selected_options[0]['value']
        else:
            value = [option['value'] for option in selected_options]
        
        fields[select['name']] = value
    
    return fields
