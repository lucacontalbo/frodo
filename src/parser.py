from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace, BNode
from rdflib.namespace import XSD
from utility import *
from functools import partial
import pprint

VOWELS = ['a','e','i','o','u','A','E','I','O','U']

class Parser:
	"""
	This class performs the parsing fred -> frodo explained in frodo's paper
	"""

	def __init__(self):
		self.fred = Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
		self.dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
		self.owl = Namespace("http://www.w3.org/2002/07/owl#")
		self.vn_data = Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/")
		self.fred_pos = Namespace("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#")
		self.frodo = Namespace("https://w3id.org/stlab/ontology/")

		self.graph = Graph()

		self.graph.bind('fred',URIRef("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"),False)
		self.graph.bind('dul',URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"),False)
		self.graph.bind('vn_data',URIRef("http://www.ontologydesignpatterns.org/ont/vn/abox/role/"),False)
		self.graph.bind('fred_quantifiers',URIRef("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"),False)
		self.graph.bind('semiotics',URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#"),False)
		self.graph.bind('earmark',URIRef("http://www.essepuntato.it/2008/12/earmark#"),False)
		self.graph.bind('fred_pos',URIRef("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#"),False)
		self.graph.bind('frodo',URIRef("https://w3id.org/stlab/ontology/"),False)

		self.agentive = [self.vn_data.Agent, self.vn_data.Actor, self.vn_data.Cause, self.vn_data.Stimulus] #list of possible agentive roles
		self.passive = [self.vn_data.Patient, self.vn_data.Experiencer, self.vn_data.Material, self.vn_data.Result, self.vn_data.Product] #list of possible passive roles

	"""
	get_frame_occ_list: recursive function which finds the instances of frame occurrences. Read Frodo's paper for the definition of frame occurrence
	Input: object(optional) -> the input is a class, treated as an object when looking for triples. The parameter is ONLY used for the recursion
				   hence this function MUST be called without the parameter for its intended use.
	Output: list of frame occurrences
	"""

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

	"""
	get_passive_role:
	Input: frame occurrence
	Output: passive role
	"""

	def get_passive_role(self,frame_occurrence):
		passive = []
		for role in self.passive:
			passive_roles = list(self.graph.objects(frame_occurrence,role))
			if len(passive_roles) != 0:
				passive.append(passive_roles[0])
		return passive

	"""
	get_agentive_role: same as get_passive_role, but for agents
	"""

	def get_agentive_role(self,frame_occurrence):
		agentive = []
		for role in self.agentive:
			agentive_roles = list(self.graph.objects(frame_occurrence,role))
			if len(agentive_roles) != 0:
				agentive.append(agentive_roles[0])
		return agentive


	def get_periphrastic_relations(self):
		filtered_periphrastic = []
		periphrastic = list(self.graph.triples((None,RDF.type,self.owl.ObjectProperty)))
		for triple in periphrastic:
			if self.fred in triple[0]:
				filtered_periphrastic.append(triple[0])
		return list(set(filtered_periphrastic)) #deleting duplicate entries

	"""
	get_role:
	Input: el -> frame_occurrence
	       role_type: agentive for returning agentive role, passive for returning passive role
	Output: passive instance, class of the passive instance and passive class name (or agentive based on role_type)
	"""

	def get_role(self,el,role_type="agentive"):
		assert role_type == "agentive" or role_type == "passive"
		if role_type == "agentive":
			agentive_roles = self.get_agentive_role(el)
			class_agentive_roles = list_map(self.graph.objects,agentive_roles,predicate=RDF.type)
			agentive_name = class_agentive_roles[0].split('#')[1]
			return agentive_roles, class_agentive_roles, agentive_name
		elif role_type == "passive":
			passive_roles = self.get_passive_role(el) #passive role associated to n-ary instance
			class_passive_roles = list_map(self.graph.objects,passive_roles,predicate=RDF.type) #TODO: can be made easier: maybe there is one passive role per n-ary relation?
			passive_name = class_passive_roles[0].split('#')[1] #name of the passive class
			return passive_roles, class_passive_roles, passive_name


	def change_name_n_ary_class(self,superclass,superclass_name):
		sub = list(self.graph.predicate_objects(superclass))
		obj = list(self.graph.subject_predicates(superclass))

		#remove every occurrence of n-ary class as subject and object
		self.graph.remove((superclass,None,None))
		self.graph.remove((None,None,superclass))

		for p,o in sub: #change existing occurrences of the n-ary class
			self.graph.add((URIRef(self.fred+superclass_name),p,o))
		for s,p in obj:
			self.graph.add((s,p,URIRef(self.fred+superclass_name)))

	"""
	n_ary_parsing: base function applying the first step of fred -> frodo's conversion
	The function has no input and output, since it modifies self.graph
	"""

	def n_ary_parsing(self):
		frame_occurrences = self.get_frame_occ_list()
		for el in frame_occurrences:
			superclass = list(self.graph.objects(el,RDF.type))[0] #n-ary class
			superclass_name = superclass.split('#')[1]

			if superclass_name[-1] in VOWELS:
				superclass_name = superclass_name[:-1]
			superclass_name+='ing'


			passive_roles, class_passive_roles, passive_name = self.get_role(el,role_type="passive")
			agentive_roles, class_agentive_roles, agentive_name = self.get_role(el,role_type="agentive")

			self.change_name_n_ary_class(superclass,superclass_name)

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

	def change_periphrastic_property_name(self,properties):
		for prop in properties:
			pred = list(self.graph.triples((None,prop,None)))

			for triple in pred:
				passive_class = list(self.graph.triples((triple[2],RDF.type,None)))[0][2]
				new_pred_name = triple[1]+passive_class.split('#')[1]
				splitted_new_pred_name = new_pred_name.split('#')
				splitted_new_pred_name[1] = splitted_new_pred_name[1][0].upper()+splitted_new_pred_name[1][1:]
				inverse_pred_name = URIRef(splitted_new_pred_name[0]+"#is{}Of".format(splitted_new_pred_name[1]))

				for s,p,o in self.graph.triples((triple[1],None,None)):
					self.graph.add((new_pred_name,p,o))
				for s,p,o in self.graph.triples((None,triple[1],None)):
					self.graph.add((s,new_pred_name,o))
					self.graph.add((o,inverse_pred_name,s)) #adding inverse relation
				for s,p,o in self.graph.triples((None,None,triple[1])):
					self.graph.add((s,p,new_pred_name))

				self.graph.remove((triple[1],None,None)) #removing old triples
				self.graph.remove((None,triple[1],None))
				self.graph.remove((None,None,triple[1]))

				self.graph.add((new_pred_name,RDFS.domain,self.owl.Thing)) #domain and range axioms
				self.graph.add((new_pred_name,RDFS.range,passive_class))

				self.graph.add((inverse_pred_name,RDF.type,self.owl.ObjectProperty)) #type, domain and range axioms for inverse
				self.graph.add((inverse_pred_name,RDFS.domain,passive_class))
				self.graph.add((inverse_pred_name,RDFS.range,self.owl.Thing))

				self.graph.add((new_pred_name,self.owl.inverseOf,inverse_pred_name))
				self.graph.add((inverse_pred_name,self.owl.inverseOf,new_pred_name))

	def periphrastic_parsing(self):
		periphrastic_relations = self.get_periphrastic_relations()
		self.change_periphrastic_property_name(periphrastic_relations)
		#change the involved class namespaces to frodo namespace

	"""
	parse: public function called for fred -> frodo's conversion
	Input: RDF/XML fred graph
	Output: RDF/XML frodo graph
	"""

	def parse(self,rdf):
		for el in rdf:
			self.graph.parse(data=el, format="application/rdf+xml")
			self.periphrastic_parsing()
			self.n_ary_parsing()
			print(self.graph.serialize(format="turtle"))
		return self.graph.serialize(format="xml")
