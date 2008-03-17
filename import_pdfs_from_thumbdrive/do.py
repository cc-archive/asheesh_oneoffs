import string
import glob
import sys
if filter(lambda f: f.endswith('pdf'), map(string.lower, glob.glob('/media/disk/*'))):
    sys.exit(0)
sys.exit(1)
