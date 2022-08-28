class Tester:
	def __init__(self,fred,parser):
		self.fred = fred
		self.parser = parser
		self.tests = ['Who commissioned a component of a system?', 'What are the contaminated sites in a geographical area recorded in time?','When is the rate of hospitalisation related to a disease registered?','Who monitors the hospitalisations for a disease in geographical area?']
	def test(self):
		rdf = self.fred.get_rdf(self.tests)
		self.parser.parse(rdf)
