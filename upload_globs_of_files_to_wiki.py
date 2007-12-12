## imports
import mechanize
import glob
import getpass

wiki_base = 'http://wiki.creativecommons.org/'
assert wiki_base[-1] == '/'

def login():
    ## login
    b = mechanize.Browser()
    b.set_handle_robots(False)
    b.open(wiki_base + 'Special:Userlogin')
    b.select_form(nr=0)
    b['wpPassword'] = getpass.getpass('hi > ').strip()
    b['wpName'] = 'paulproteus'
    b.submit()
    return b

def upload_glob(b, glob_me = '*'):
    ## uploading
    for file in glob.glob(glob_me):
        b.open(wiki_base + 'Special:Upload')
        b.select_form(nr=0)
        b.add_file(open(file), 'image/svg+xml', file)
        b['wpDestFile'] = file
        b.submit()
        b.select_form(nr=0)
        b.submit()
    
