from rdf2graph import Rdf2Graph

class Tester:
	def __init__(self,fred,parser,competency_question,save_path):
		self.fred = fred
		self.parser = parser
		self.competency_question = competency_question
		self.rdf2graph = Rdf2Graph(save_path)

	def test(self):
		rdf = self.fred.get_rdf([self.competency_question])
		print(rdf)
		frodo_rdf = self.parser.parse(rdf)
		print("----- OBTAINED ONTOLOGY -----")
		print(frodo_rdf)
		if self.rdf2graph.get_save_path() != '':
			self.rdf2graph.visualize(frodo_rdf,self.parser.get_outtype())
