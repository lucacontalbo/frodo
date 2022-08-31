from rdf2graph import Rdf2Graph

DISPLAY_PNG = True
SAVE_PNG = True

class Tester:
	def __init__(self,fred,parser):
		self.fred = fred
		self.parser = parser
		self.rdf2graph = Rdf2Graph()
		self.tests = ['Who commissioned a component of a system?', 'What are the contaminated sites in a geographical area recorded in time?','When is the rate of hospitalisation related to a disease registered?','Who monitors the hospitalisations for a disease in geographical area?']
	def test(self):
		rdf = self.fred.get_rdf([self.tests[0]])
		frodo_rdf = self.parser.parse(rdf)
		"""if DISPLAY_PNG:
			if SAVE_PNG:
				self.rdf2graph.get_png(frodo_rdf,file_name=self.tests[0].replace(' ',''))
			else:
				self.rdf2graph.get_png(frodo_rdf)
		"""
