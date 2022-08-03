from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace
from rdflib.namespace import XSD
from utility import *
import pprint

class parser:
	def __init__(self):
		self.fred = Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
		self.dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
		self.vn_data = Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/")

		self.graph = Graph()

		self.graph.bind('fred',URIRef("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"),False)
		self.graph.bind('dul',URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"),False)
		self.graph.bind('vn_data',URIRef("http://www.ontologydesignpatterns.org/ont/vn/abox/role/"),False)
		self.graph.bind('fred_quantifiers',URIRef("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"),False)
		self.graph.bind('semiotics',URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#"),False)
		self.graph.bind('earmark',URIRef("http://www.essepuntato.it/2008/12/earmark#"),False)
		self.graph.bind('fred_pos',URIRef("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#"),False)

	def n_ary_parsing(self,object=None):
		list = []
		if object == None:
			for s,p,o in self.graph.triples((None,RDFS.subClassOf,self.dul.Event)):
				list.extend(self.n_ary_parsing(s))
		else:
			for s,p,o in self.graph.triples((None,RDFS.subClassOf,object)):
				list.extend(self.n_ary_parsing(s))
			for s,p,o in self.graph.triples((None,RDF.type,object)):
				list.append(s)
		return list

	def parse(self,rdf):
		self.graph.parse(data=rdf, format="application/rdf+xml")
		frame_occurrences = self.n_ary_parsing()
		print(frame_occurrences)

		
		#print(self.graph.serialize(format="turtle"))
		#if (None,RDFS.subClassOf,self.dul.Event) in self.graph:
		#	print("found")
