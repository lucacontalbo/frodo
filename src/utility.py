from functools import partial

def flatten(list): #matrix to list
	return [item for sublist in list for item in sublist]

def list_map(function,lst,**args): #apply function to each element of list and return a list
	return list(list(map(partial(function,**args),lst))[0])

def get_changed_namespace(str,prefix,delimeter='#'):
	return prefix+str.rsplit(delimeter,1)[1]

def set_tuple(tupl,idx,element):
	tupl = list(tupl)
	tupl[idx] = element
	return tuple(tupl)

