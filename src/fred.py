from subprocess import check_output
import subprocess

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
			rdfs.append(subprocess.Popen('curl -G -H "Authorization: Bearer '+self.token+' " -H "Accept: application/rdf+xml" --data-urlencode text="'+text+'" http://wit.istc.cnr.it/stlab-tools/fred',shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8"))
		return rdfs
