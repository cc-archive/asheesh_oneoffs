input = ''

def dude2key(dude):
    dude = dude.replace('[[', '')
    dude = dude.replace(']]', '')
    dude = dude.split(',')[0]
    names = dude.split(' ')
    names.reverse()
    return names

def sort_list_of_dudes(dudes):
	dudes_with_meta = [ (dude2key(dude), dude) for dude in dudes]
	dudes_with_meta.sort()
	return [dude for meta, dude in dudes_with_meta]

def expand(s):
	return s.split('\n\n')

def collapse(l):
	return '\n\n'.join(l)

print collapse(sort_list_of_dudes(expand(input.strip())))

