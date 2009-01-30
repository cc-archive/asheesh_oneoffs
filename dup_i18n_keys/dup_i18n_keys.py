import babel.messages.pofile
import collections

def main():
    import sys
    print find_dup_keys(open(sys.argv[1]))

def find_dup_keys(fd):
    duplicate = set()

    pofile = babel.messages.pofile.read_po(fd)
    keys = list(pofile._messages.keys())

    # If it's a tuple, replace it with it[0]
    for key in keys:
        assert type(key) == unicode

    # Create a mapping that groups equivalent (but for case) translations
    key2xlation = collections.defaultdict(list)
    for key in keys:
        key2xlation[key.lower()].append(pofile[key].string)

    for key in key2xlation:
        if len(key2xlation[key]) > 1:
            # Assert all the translations are the same
            for xlation in key2xlation[key]:
                assert xlation == key2xlation[key][0]

            # Life is good.
            duplicate.add(key)

    return duplicate

if __name__ == '__main__':
    main()

