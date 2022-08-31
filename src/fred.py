from subprocess import check_output
import subprocess

AUTO = False #True: queries fred to obtain rdf, False: takes the rdf graph from file

class Fred:
	def __init__(self):
		with open('../token') as f:
			lines = f.readlines()
			lines = lines[0].rstrip('\n')
		self.token = lines

	def get_rdf(self,lst_text):
		#TODO: suppress output
		rdfs = []
		for text in lst_text:
			if AUTO:
				rdfs.append(subprocess.Popen('curl -G -H "Authorization: Bearer '+self.token+' " -H "Accept: application/rdf+xml" --data-urlencode text="'+text+'" http://wit.istc.cnr.it/stlab-tools/fred',shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8"))
			else:
				for text in lst_text:
					rdf = text.replace(' ','')
					with open('./saved_rdfs/{0}'.format(rdf)) as f:
						rdf = ''.join(f.readlines())
						rdfs.append(rdf)
		return rdfs
