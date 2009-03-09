import babel.messages.pofile
import collections
import dup_i18n_keys

def main():
    import sys
    filename, duplicates = sys.argv[1], sys.argv[2:]
    print 'Going to remove', duplicates, 'from', filename
    remove_dup_keys(filename, duplicates)
    print 'YOW! Finished.'

def remove_dup_keys(filename, remove_this):
    # Verify that each of the remove_this things all the duplicates
    remove_this = set(remove_this)

    # Actually remove
    pofile = babel.messages.pofile.read_po(open(filename))
    for key in remove_this:
        del pofile._messages[key]

    # Now recklessly clobber that input filename
    out_fd = open(filename, 'w')
    babel.messages.pofile.write_po(out_fd, pofile)

if __name__ == '__main__':
    main()

