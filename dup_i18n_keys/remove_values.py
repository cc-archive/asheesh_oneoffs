import babel.messages.pofile
import collections

def main():
    import sys
    filename = sys.argv[1]
    print 'Going to remove values from', filename
    remove_values(filename)
    print 'YOW! Finished.'

def remove_values(filename):
    # Verify that each of the remove_this things all the duplicates

    # Actually remove
    pofile = babel.messages.pofile.read_po(open(filename))
    for key in pofile._messages:
        pofile._messages[key].string = ''

    # Now recklessly clobber that input filename
    out_fd = open(filename, 'w')
    babel.messages.pofile.write_po(out_fd, pofile)
    out_fd.close()

if __name__ == '__main__':
    main()

