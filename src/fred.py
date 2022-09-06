from subprocess import check_output
import subprocess

class Fred:
	def __init__(self,auto):
		self.AUTO = auto #True: queries fred to obtain rdf, False: takes the rdf graph from file
				 #in the latter case, the filename must be the competency question question without spaces and without extension
		with open('./token') as f:
			lines = f.readlines()
			lines = lines[0].rstrip('\n')
		self.token = lines

	def get_rdf(self,lst_text):
		#TODO: suppress output
		rdfs = []
		for text in lst_text:
			if self.AUTO:
				try:
					rdfs.append(subprocess.Popen('curl -G -H "Authorization: Bearer '+self.token+' " -H "Accept: application/rdf+xml" --data-urlencode text="'+text+'" http://wit.istc.cnr.it/stlab-tools/fred',shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8"))
					if len(rdfs) == 1 and rdfs[0] == '':
						raise
				except:
					print("The endpoint seems to be down. Follow the instructions given in README.md to use pre-saved rdfs ontologies")
			else:
				for text in lst_text:
					rdf = text.replace(' ','')
					with open('./saved_rdfs/{}'.format(rdf)) as f:
						rdf = ''.join(f.readlines())
						rdfs.append(rdf)
		return rdfs
