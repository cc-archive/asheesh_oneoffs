SOURCE_CSV="/tmp/ccLearn Data.csv"
import csv
import string
import re

PAGE_TITLE, FREE_TEXT = range(2)

def organization_type_fixup(s):
    fixups = {"commercial site":"commercial",
              "governmental organization":"government organization",
              "software tool": "software",
              "volunteersourcing": "initiative",
              "3D platform": "platform"}
    l = s.split(',')
    return [fixups.get(original, original) 
            for original in l]

def identity(if_empty = None):
    def _identity(thing):
        ret = thing
        if if_empty is not None:
            if not thing.strip():
                ret = if_empty
        return [thing]
    return _identity

def url_fixup(thing):
    if not thing:
        return []
    list_of_things = [thing]
    if ',' in thing or ';' in thing:
        list_of_things = map(string.strip, re.split('[;,]', thing))
    ret = map(url_fixup_one, list_of_things)
    for element in ret:
        assert element.count('://') <= 1
    return ret
        
def url_fixup_one(thing):
    ret = thing
    if not thing.startswith('http://') and not thing.startswith('https://'):
        ret = 'http://' + thing
        print 'Upgraded', ret, 'to a proper HTTP URI'
    assert ret.count('://') <= 1
    assert ',' not in ret
    return ret

status_fixup = identity('good')
open_free_fixup = identity('no')

cols2template = {
    0: (PAGE_TITLE, identity()),
    1: ('Affiliation', identity()),
    2: ('Affiliation', identity()),
    3: ('Affiliation', identity()),
    4: ('Affiliation', identity()),
    5: ('Mainurl', identity()),
    6: ('Resource URL', url_fixup),
    7: ('Tag', lambda s: [t.strip() for t in s.split()]),
    8: ('Organization Type', organization_type_fixup),
    9: ('Status', status_fixup),
    10:(FREE_TEXT, identity()),
    11:("Open or Free Statement", open_free_fixup),
    12:("License provider", identity('')),
    13:("License short name", identity()),
    14:("License", url_fixup)
    }

def dict2template(indict):
    ''' Input: a dictionary
    Output: A MW template string'''
    mydict = indict.copy()

    page_title = mydict[PAGE_TITLE]
    del mydict[PAGE_TITLE]
    free_text = mydict[FREE_TEXT]
    del mydict[FREE_TEXT]

    print 'For page with title', page_title

    ret = '{{Organization\n'
    for elt in mydict:
        ret += '|' + elt + '=' + mydict[elt] + "\n"
    ret += "}}\n"
    if free_text:
        ret += '\n' + free_text + '\n'
        
    return ret

def row2dict(row):
    '''Input: a list of entries in the row
    Output: a dict with a mapping of MW template parameter name
    to a list (sometimes of length 1) of values for it
    '''
    data = {}
    for index, value in enumerate(row):
        name, function = cols2template[index]
        data[name] = ','.join(function(value))
    return data

def main():
    csv_stream = csv.reader(open(SOURCE_CSV))
    for row in csv_stream:
        data = row2dict(row)
        print dict2template(data)

    
