import lxml.html
import urllib2
import urlparse
BASE='http://translate.creativecommons.org/'


def languages(root):
    langs = set()
    for link in root.cssselect('.language a'):
        href = link.get('href')
        if href.count('/') == 1:
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
    assert '?' not in lang_project_url
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
        name_text = ''.join(name_col.itertext())
        if 'pootle' in name_text.lower():
            continue
        if 'terminology' in name_text.lower():
            continue

        # The name_col will have a link...
        link = name_col.find('a').get('href')
        if lang_project_has_suggestions(urlparse.urljoin(lang_url, link)):
            return True
        # Otherwise try the next one.

    return False

def long_lang_name(short_lang_name):
    if '://' not in short_lang_name:
        url = urlparse.urljoin(BASE, short_lang_name)
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
        if lang.endswith('templates/'):
            continue # Skip templates

        short_lang, value = lang.split('/')[0], lang2percent(lang)
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

        short_lang, value = lang.split('/')[0], lang_has_suggestions_anywhere(lang)
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
    print format_precents(percents, suggestion_data)


if __name__ == '__main__':
    main()
