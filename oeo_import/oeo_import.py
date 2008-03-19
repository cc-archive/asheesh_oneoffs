SOURCE_CSV="/tmp/ccLearn Data.csv"
import csv
import string
import urllib
import re
import os

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
        ret = ' '.join(ret.split())
        return [ret]
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

def fixup_dict_for_license(mutable_dict):
    did_anything = False
    if mutable_dict['License provider'] == 'copyright':
        did_anything = True
        mutable_dict['License provider'] = 'none'
        mutable_dict['License short name'] = 'copyright'
    if mutable_dict['License short name'] == 'various':
        if mutable_dict['License provider'] != 'CC':
            mutable_dict['License short name']=''
            did_anything = True
    if did_anything:
        print 'We fixed', mutable_dict
    

cols2template = {
    0: (PAGE_TITLE, identity()),
    1: ('Affiliation', identity()),
    2: ('Affiliation', identity()),
    3: ('Affiliation', identity()),
    4: ('Affiliation', identity()),
    5: ('Mainurl', identity()),
    6: ('Resource URL', url_fixup),
    7: ('Tag', lambda s: [t.strip() for t in s.split(',')]),
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

    ret = '{{Organization\n'
    for elt in mydict:
        ret += '|' + elt + '=' + mydict[elt] + "\n"
    ret += "}}\n"
    if free_text:
        ret += '\n' + free_text + '\n'

    return (page_title, ret)

def row2dict(row):
    '''Input: a list of entries in the row
    Output: a dict with a mapping of MW template parameter name
    to a list (sometimes of length 1) of values for it
    '''
    data = {}
    for index, value in enumerate(row):
        name, function = cols2template[index]
        if name not in data:
            data[name] = []
        data[name].extend(function(value))

    # Comma-join everything
    for name in data:
        non_empty = [thing for thing in data[name] if thing]
        data[name] = ','.join(non_empty)
        assert ',,' not in data[name]

    # Last-minute emails from Jane about license format
    fixup_dict_for_license(data)

    return data

def main():
    csv_stream = csv.reader(open(SOURCE_CSV))
    for row in csv_stream:
        data = row2dict(row)
        title, contents = dict2template(data)
        if title == 'Title/ Organization': # header row
            continue
        if not title: # When I have nothing to say, my lips are sealed
            continue
        filename = urllib.quote_plus(title) + '.mw'
        assert not os.path.exists(filename)
        fd = open(filename, 'w')
        fd.write(contents)
        fd.close()
        
if __name__ == '__main__':
    main()

        

    
