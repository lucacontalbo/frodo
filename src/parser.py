from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace
from rdflib.namespace import XSD
from utility import *
import pprint

VOWELS = ['a','e','i','o','u','A','E','I','O','U']

class Parser:
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

	def get_frame_occ_list(self,object=None):
		list = []
		if object == None:
			for s,p,o in self.graph.triples((None,RDFS.subClassOf,self.dul.Event)):
				list.extend(self.get_frame_occ_list(s))
		else:
			for s,p,o in self.graph.triples((None,RDFS.subClassOf,object)):
				list.extend(self.get_frame_occ_list(s))
			for s,p,o in self.graph.triples((None,RDF.type,object)):
				list.append(s)
		return list

	def get_passive_roles(self,frame_occurrences):
		passive = []
		i=0
		while i<len(frame_occurrences):
			passive_roles = list(self.graph.objects(frame_occurrences[i],self.vn_data.Patient))
			if len(passive_roles) == 0:
				del frame_occurrences[i]
				i-=1
			else:
				passive.append(passive_roles[0])
			i+=1
		return passive

	def n_ary_parsing(self,object=None):
		frame_occurrences = self.get_frame_occ_list()
		passive_roles = self.get_passive_roles(frame_occurrences)
		for el in frame_occurrences:
			superclass = self.graph.objects(el,RDF.type)
			superclass = list(superclass)[0]
			father = superclass.split('#')[1]
			sub,obj = [],[]
			sub.append(self.graph.predicate_objects(superclass))
			obj.append(self.graph.subject_predicates(superclass))
			sub = list(sub[0]) #can be refactored
			obj = list(obj[0])
			self.graph.remove((superclass,None,None))
			self.graph.remove((None,None,superclass))
			if father[-1] in VOWELS:
				father = father[:-1]
			father+='ing'
			for p,o in sub:
				self.graph.add((URIRef(self.fred+father),p,o))
			for s,p in obj:
				self.graph.add((s,p,URIRef(self.fred+father)))

	def parse(self,rdf):
		for el in rdf:
			self.graph.parse(data=el, format="application/rdf+xml")
			self.n_ary_parsing()
		
			print(self.graph.serialize(format="turtle"))
