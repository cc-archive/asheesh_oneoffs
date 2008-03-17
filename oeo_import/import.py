SOURCE_CSV="/tmp/ccLearn Data.csv"

PAGE_TITLE, FREE_TEXT = range(2)

def organization_type_fixup(s):
    fixups = {"commercial site":"commercial",
              "governmental organization":"government organization",
              "software tool": "software",
              "volunteersourcing": "initiative",
              "3D platform": "platform"}
    l = s.split(',')
    return [fixups.get(elt, original) 
            for original in l]

def identity(if_empty = None):
    def _identity(thing):
        ret = thing
        if if_empty is not None:
            if not thing.strip():
                ret = if_empty
        return thing
    return _identity

def url_fixup(thing):
    ret = thing
    if not thing.startswith('http://'):
        ret = 'http://' + thing
        print 'Upgraded', ret, 'to a proper HTTP URI'
    assert ret.count('://' == 1)
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
    7: ('Tag', lambda s: [t.strip() for t in t.split()]),
    8: ('Organization Type', organization_type_fixup),
    9: ('Status', status_fixup),
    10:(FREE_TEXT, identity),
    11:("Open or Free Statement", open_free_fixup),
    12:("License provider", identity('')),
    13:("License short name", identity()),
    14:("License", url_fixup)
    }

def row2dict(row):
    '''Input: a list of entries in the row
    Output: a dict with a mapping of MW template parameter name
    to a list (sometimes of length 1) of values for it
    '''
    pass
