from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace, BNode
from rdflib.namespace import XSD
from utility import *
from functools import partial
import pprint

VOWELS = ['a','e','i','o','u','A','E','I','O','U']

class Parser:
	def __init__(self):
		self.fred = Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
		self.dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
		self.owl = Namespace("http://www.w3.org/2002/07/owl#")
		self.vn_data = Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/")
		self.fred_pos = Namespace("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#")

		self.graph = Graph()

		self.graph.bind('fred',URIRef("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"),False)
		self.graph.bind('dul',URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"),False)
		self.graph.bind('vn_data',URIRef("http://www.ontologydesignpatterns.org/ont/vn/abox/role/"),False)
		self.graph.bind('fred_quantifiers',URIRef("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"),False)
		self.graph.bind('semiotics',URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#"),False)
		self.graph.bind('earmark',URIRef("http://www.essepuntato.it/2008/12/earmark#"),False)
		self.graph.bind('fred_pos',URIRef("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#"),False)

		self.agentive = [self.vn_data.Agent, self.vn_data.Actor, self.vn_data.Cause, self.vn_data.Stimulus]
		self.passive = [self.vn_data.Patient, self.vn_data.Experiencer, self.vn_data.Material, self.vn_data.Result, self.vn_data.Product]

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

	def get_passive_role(self,frame_occurrence):
		passive = []
		for role in self.passive:
			passive_roles = list(self.graph.objects(frame_occurrence,role))
			if len(passive_roles) != 0:
				passive.append(passive_roles[0])
		return passive

	def get_agentive_role(self,frame_occurrence):
		agentive = []
		for role in self.agentive:
			agentive_roles = list(self.graph.objects(frame_occurrence,role))
			if len(agentive_roles) != 0:
				agentive.append(agentive_roles[0])
		return agentive


	def get_periphrastic_relations(self):
		periphrastic = self.graph.triples((None,RDF.type,self.owl.ObjectProperty))
		#TODO: filter by fred's namespace
		return periphrastic

	def n_ary_parsing(self,object=None):
		frame_occurrences = self.get_frame_occ_list()
		for el in frame_occurrences:
			superclass = list(self.graph.objects(el,RDF.type))[0] #n-ary class
			superclass_name = superclass.split('#')[1]

			passive_roles = self.get_passive_role(el) #passive role associated to n-ary instance
			class_passive_roles = list_map(self.graph.objects,passive_roles,predicate=RDF.type) #TODO: can be made easier: maybe there is one passive role per n-ary relation?
			passive_name = class_passive_roles[0].split('#')[1] #name of the passive class

			agentive_roles = self.get_agentive_role(el)
			class_agentive_roles = list_map(self.graph.objects,agentive_roles,predicate=RDF.type)
			agentive_name = class_agentive_roles[0].split('#')[1]

			sub,obj = [],[]
			sub.append(self.graph.predicate_objects(superclass))
			obj.append(self.graph.subject_predicates(superclass))
			sub = list(sub[0]) #TODO: can be refactored
			obj = list(obj[0])

			#remove every occurrence of n-ary class as subject and object
			self.graph.remove((superclass,None,None))
			self.graph.remove((None,None,superclass))

			if superclass_name[-1] in VOWELS:
				superclass_name = superclass_name[:-1]
			superclass_name+='ing'

			for p,o in sub: #change existing occurrences of the n-ary class
				self.graph.add((URIRef(self.fred+superclass_name),p,o))
			for s,p in obj:
				self.graph.add((s,p,URIRef(self.fred+superclass_name)))

			#add n-ary class
			self.graph.add((URIRef(self.fred+passive_name+superclass_name),RDFS.subClassOf,URIRef(self.fred+superclass_name)))

			#fred doesn't put, for each class, the triple showing that it is an instance of owl:Class, so no such triple will be added in FRODO

			#change type of n-ary instance
			self.graph.remove((el,RDF.type,None))
			self.graph.add((el,RDF.type,URIRef(self.fred+passive_name+superclass_name)))

			#change property names
			for passive_role in self.passive:
				self.graph.remove((el,passive_role,None))
			for agent_role in self.agentive:
				self.graph.remove((el,agent_role,None))

			self.graph.add((URIRef(self.fred+'involves{}'.format(agentive_name)),RDF.type,self.owl.ObjectProperty)) #setting new relations as properties
			self.graph.add((URIRef(self.fred+'involves{}'.format(passive_name)),RDF.type,self.owl.ObjectProperty))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)),RDF.type,self.owl.ObjectProperty))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(passive_name)),RDF.type,self.owl.ObjectProperty))

			self.graph.add((URIRef(self.fred+'involves{}'.format(agentive_name)),RDFS.domain,self.owl.Thing)) #setting domain axioms to properties
			self.graph.add((URIRef(self.fred+'involves{}'.format(passive_name)),RDFS.domain,self.owl.Thing))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)),RDFS.domain,class_agentive_roles[0]))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(passive_name)),RDFS.domain,class_passive_roles[0]))

			self.graph.add((URIRef(self.fred+'involves{}'.format(agentive_name)),RDFS.range,class_agentive_roles[0])) #setting range axioms to properties
			self.graph.add((URIRef(self.fred+'involves{}'.format(passive_name)),RDFS.range,class_passive_roles[0]))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)),RDFS.range,self.owl.Thing))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(passive_name)),RDFS.range,self.owl.Thing))

			self.graph.add((URIRef(self.fred+'involves{}'.format(agentive_name)),self.owl.inverseOf,URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)))) #setting inverseOf relations
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)),self.owl.inverseOf,URIRef(self.fred+'involves{}'.format(agentive_name))))
			self.graph.add((URIRef(self.fred+'involves{}'.format(passive_name)),self.owl.inverseOf,URIRef(self.fred+'is{}InvolvedIn'.format(passive_name))))
			self.graph.add((URIRef(self.fred+'is{}InvolvedIn'.format(passive_name)),self.owl.inverseOf,URIRef(self.fred+'involves{}'.format(passive_name))))

			self.graph.add((el,URIRef(self.fred+'involves{}'.format(agentive_name)),agentive_roles[0])) #setting newly created properties between class instances
			self.graph.add((el,URIRef(self.fred+'involves{}'.format(passive_name)),passive_roles[0]))

			self.graph.add((agentive_roles[0],URIRef(self.fred+'is{}InvolvedIn'.format(agentive_name)),el))
			self.graph.add((passive_roles[0],URIRef(self.fred+'is{}InvolvedIn'.format(passive_name)),el))

			#adding subclass restrictions to newly created class
			blank_node1 = BNode()

			self.graph.add((blank_node1,RDF.type,self.owl.Restriction))
			self.graph.add((blank_node1,self.owl.onProperty,URIRef(self.fred+'involves{}'.format(agentive_name))))
			self.graph.add((blank_node1,self.owl.someValuesFrom, URIRef(self.fred+'involves{}'.format(agentive_name)))) #someValuesFrom and allValuesFrom should be the same, given the range axioms of the properties

			blank_node2 = BNode()

			self.graph.add((blank_node2,RDF.type,self.owl.Restriction))
			self.graph.add((blank_node2,self.owl.onProperty,URIRef(self.fred+'involves{}'.format(passive_name))))
			self.graph.add((blank_node2,self.owl.someValuesFrom, URIRef(self.fred+'involves{}'.format(passive_name))))

			self.graph.add((URIRef(self.fred+passive_name+superclass_name),RDFS.subClassOf,blank_node1))
			self.graph.add((URIRef(self.fred+passive_name+superclass_name),RDFS.subClassOf,blank_node2))

		#TODO: change class namespaces to frodo namespaces

	def periphrastic_parsing(self):
		periphrastic_relations = self.get_periphrastic_relations()
		#change relation name following template described in paper
		#change the involved class namespaces to frodo namespace
		#define range axioms
		#define inverse relations

	def parse(self,rdf):
		for el in rdf:
			self.graph.parse(data=el, format="application/rdf+xml")
			self.n_ary_parsing()
			self.periphrastic_parsing()
			print(self.graph.serialize(format="turtle"))
