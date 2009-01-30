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
        if type(key) == type( () ):
            keys.replace(key, key[0])

    # Create a bag that shows the counts of the keys' lower-cased values
    key2count = collections.defaultdict(int)
    for key in keys:
        key2count[key.lower()] += 1

    for key in key2count:
        if key2count[key] > 1:
            duplicate.add(key)

    return duplicate

if __name__ == '__main__':
    main()

