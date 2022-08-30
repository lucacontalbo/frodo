from functools import partial

def flatten(list): #matrix to list
	return [item for sublist in list for item in sublist]

def list_map(function,lst,**args):
	return list(list(map(partial(function,**args),lst))[0])

