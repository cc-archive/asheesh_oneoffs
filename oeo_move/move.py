'''Mission:
Given a CC Wiki dump, remove all the pages that only have an Organization template in them.

For the pages that have an Organization template in them, as well as somethinge else,
just replace the Organization template with the empty string and move on.'''

import xml.dom.minidom
import re
import urllib
import codecs

DUMP_PATH='/tmp/dump.xml'
ORG_REGEX_S = r'{{Organization.*?}}\s*'
ORG_REGEX = re.compile(ORG_REGEX_S, re.DOTALL)

# We're lucky that our CC Wiki dump can fit in memory when parsed with the DOM.
def remove_org_from_text(text):
    '''Returns a page's text without the Organization template.'''
    return ORG_REGEX.sub('', text)

def main():
    parsed = xml.dom.minidom.parse(DUMP_PATH)
    for page in parsed.getElementsByTagName('page'):
        title = page.getElementsByTagName('title')[0].childNodes[0].wholeText.encode('utf-8')
        text_node = page.getElementsByTagName('text')[0]
        if text_node.childNodes:
            text = text_node.childNodes[0].wholeText
        else:
            continue # can't do anything with this particular page
        cleaned_text = remove_org_from_text(text)
        if cleaned_text.strip() == '':
            print 'should delete', title
        elif cleaned_text != text:
            print 'should modify', title
            escaped_title = urllib.quote(title)
            fd = codecs.open('changed/' + escaped_title + '.mw', 'w', 'utf-8')
            fd.write(cleaned_text)
            fd.close()

if __name__ == '__main__':
    main()
