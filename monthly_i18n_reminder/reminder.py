import lxml.html
import email
import email.charset
import email.mime.text
import smtplib
import urllib2
import urlparse
BASE='http://translate.creativecommons.org/projects/cc_org/'

def send_mail(subject, body, dry_run = False):
    # Create a UTF-8 quoted printable encoder
    charset = email.charset.Charset('utf-8')
    charset.header_encoding = email.charset.QP
    charset.body_encoding = email.charset.QP

    # Jam the data into msg, as binary utf-8
    msg = email.mime.text.MIMEText(body, 'plain')

    # Message class computes the wrong type from MIMEText constructor,
    # which does not take a Charset object as initializer. Reset the
    # encoding type to force a new, valid evaluation
    del msg['Content-Transfer-Encoding']
    msg.set_charset(charset) 
    msg.set_param('format', 'flowed')
    msg.add_header('Subject', subject)
    SERVER='localhost'
    FROM='"Monthly Translation Update" <asheesh@creativecommons.org>'
    if dry_run:
        TO = ['asheesh@creativecommons.org']
    else:
        TO = ['cci@lists.ibiblio.org']

    msg.add_header('To', TO[0])

    s = smtplib.SMTP()
    s.connect(SERVER)
    s.sendmail(FROM, TO, msg.as_string())
    if dry_run:
        print msg.as_string()
    s.close()

def url2parts(url):
    type, domain, path, _, _, _ = urlparse.urlparse(url)
    if path[0] == '/':
        path = path[1:]
    if path[-1] == '/':
        path = path[:-1]

    assert path.endswith('cc_org'), path
    first, rest = path.rsplit('/', 1)
    lang_code = first.split('/')[-1]
    return dict(lang_path=first, lang_code=lang_code, project=rest)

def languages(root):
    langs = set()
    for link in root.cssselect('.stats-name a'):
        href = link.get('href')
        if True or (href.count('/') in (1,2)):
            langs.add(href)
    return langs

def parse(url):
    doc = urllib2.urlopen(url).read()
    return lxml.html.fromstring(doc)

def lang2percent(lang_url):
    '''Input: a language URL
    Output: percentage, a float of (100 * xlated words / total words)'''
    if '://' not in lang_url:
        lang_url = urlparse.urljoin(BASE, lang_url)

    # Parse this
    parsed = parse(lang_url)
    
    # Grab the stats table rows
    rows = parsed.cssselect('.stats tbody tr')

    total_words = 0
    xlated_words = 0

    for name_col, progress_col, summary_col, total_words_col in rows:
        # If this is the Pootle or Terminology project, skip this row
        name_text = ''.join(name_col.itertext())
        if 'pootle' in name_text.lower():
            continue
        if 'terminology' in name_text.lower():
            continue

        # Grab the word count for this project (AKA row)
        this_row_word_count = int(''.join(total_words_col.itertext()))
        
        # Jam that on so we can calculate
        total_words += this_row_word_count

        # How many are translated?
        summary_col_text = ''.join(summary_col.itertext()).strip()
        if 'Complete' in summary_col_text:
            xlated_words += this_row_word_count
        else: # text scrape
            summary_lines = summary_col_text.split('\n')
            untranslated_count = 0
            fuzzy_count = 0

            for line in summary_lines:
                if 'fuzzy words' in line:
                    fuzzy_count = int(line.split()[0])
                elif 'untranslated words' in line:
                    untranslated_count = int(line.split()[0])

            xlated_words += this_row_word_count - untranslated_count - fuzzy_count

    return ( 100 * float(xlated_words) / total_words )

def lang_project_has_suggestions(lang_project_url):
    assert '://' in lang_project_url
    assert '?' not in lang_project_url, lang_project_url
    editing_functions_url = lang_project_url + '?editing=1'
    
    # Grab it, and look for the string 'View Suggestions'
    return 'View Suggestions' in urllib2.urlopen(editing_functions_url).read()

def lang_has_suggestions_anywhere(lang_url):
    '''Input: a short language name
    Output: a boolean: Are there suggestions anywhere in this language?'''
    if '://' not in lang_url:
        lang_url = urlparse.urljoin(BASE, lang_url)

    # Parse this
    parsed = parse(lang_url)
    
    # Grab the stats table rows
    rows = parsed.cssselect('.stats tbody tr')

    for name_col, progress_col, summary_col, total_words_col in rows:
        # If this is the Pootle or Terminology project, skip this row
        name_text = ''.join(name_col.itertext()).strip()
        if name_text != 'cc_org':
            continue
        assert name_text == 'cc_org', name_text
        # The name_col will have a link...
        link = name_col.find('a').get('href') # but we don't care
        if lang_project_has_suggestions(lang_url):
            return True
        # Otherwise try the next one.

    return False

def long_lang_name(short_lang_name):
    if '://' not in short_lang_name:
        url = urlparse.urljoin(BASE, './' + short_lang_name)
    else:
        url = short_lang_name

    parsed = parse(url)
    just_relevant_link = parsed.cssselect('.title a')[0]
    return ''.join(just_relevant_link.itertext())

def generate_percents():
    ret = {}
    parsed = parse(BASE)
    langs = languages(parsed)
    for lang in langs:
        pieces = url2parts(lang)
        if pieces['lang_code'] == 'templates':
            continue # Skip templates
    
        short_lang, value = pieces['lang_code'], lang2percent(pieces['lang_path'])
        long_lang = long_lang_name(short_lang)
        ret[long_lang] = value
    return ret

def generate_suggestion_data():
    ret = {}
    parsed = parse(BASE)
    langs = languages(parsed)
    for lang in langs:
        if lang.endswith('templates/'):
            continue # Skip templates

        pieces = url2parts(lang)
        if pieces['lang_code'] == 'templates':
            continue # Skip templates
        short_lang, value = pieces['lang_code'], lang_has_suggestions_anywhere(pieces['lang_path'])
        long_lang = long_lang_name(short_lang)
        ret[long_lang] = value
    return ret

def format_precents(lang2percent, lang2suggestions):
    prefix = '''
This is a summary of what translations need some work at 
translate.creativecommons.org. We send these out at the end of every month.

(If you need help using Pootle, take a look at our documentation that
we link to as "Overview of using Pootle from the front page of
translate.creativecommons.org.)

TRANSLATION STATUS

'''.strip()

    language_data = []
    items_alpha_sorted = sorted(lang2percent.items())
    items_resorted_by_descending_percent_done = sorted(items_alpha_sorted, key=lambda thing: thing[1], reverse=True)
    for language, doneness in items_resorted_by_descending_percent_done:
        doneness = int(doneness)
        if doneness == 100:
            suffix = ', thank you!'
        else:
            suffix = ''

        if lang2suggestions[language]:
            suffix = ' (Suggestions available)' + suffix

        language_data.append(
            '%s: %d%% done%s' % (
                language, doneness, suffix))

    message = prefix + '\n\n' + '\n'.join(
        language_data)

    return message

def main():
    suggestion_data = generate_suggestion_data()
    percents = generate_percents()
    send_mail('Monthly translation status', format_precents(percents, suggestion_data), dry_run = True)


if __name__ == '__main__':
    main()
