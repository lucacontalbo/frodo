from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace, BNode
from rdflib.namespace import XSD
from utility import *
from functools import partial
from copy import deepcopy
import pprint

VOWELS = ['a','e','i','o','u','A','E','I','O','U']

class Parser:
	"""
	This class performs the parsing fred -> frodo explained in frodo's paper
	outtype: output syntax of the obtained ontology
	simplify: boolean value, whether to get rid of some FRED's meta data or not
	"""

	def __init__(self,outtype,simplify):
		self.fred = Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
		self.dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
		self.owl = Namespace("http://www.w3.org/2002/07/owl#")
		self.vn_data = Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/")
		self.fred_pos = Namespace("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#")
		self.frodo = Namespace("https://w3id.org/stlab/ontology/")
		self.boxer = Namespace("http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#")
		self.semiotics = Namespace("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#")
		self.earmark = Namespace("http://www.essepuntato.it/2008/12/earmark#")

		self.graph = Graph()

		self.graph.bind('dul',URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"),False)
		self.graph.bind('vn_data',URIRef("http://www.ontologydesignpatterns.org/ont/vn/abox/role/"),False)
		self.graph.bind('fred_quantifiers',URIRef("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"),False)
		self.graph.bind('semiotics',URIRef("http://ontologydesignpatterns.org/cp/owl/semiotics.owl#"),False)
		self.graph.bind('earmark',URIRef("http://www.essepuntato.it/2008/12/earmark#"),False)
		self.graph.bind('fred_pos',URIRef("http://www.ontologydesignpatterns.org/ont/fred/pos.owl#"),False)
		self.graph.bind('frodo',URIRef("https://w3id.org/stlab/ontology/"),False)
		self.graph.bind('fred',URIRef("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"),False)
		self.graph.bind('boxer',URIRef("http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#"),False)

		self.agentive = [self.vn_data.Agent, self.vn_data.Actor, self.vn_data.Cause, self.vn_data.Stimulus, self.boxer.agent] #list of possible agentive roles
		self.passive = [self.vn_data.Patient, self.vn_data.Experiencer, self.vn_data.Material, self.vn_data.Result, self.vn_data.Product, self.boxer.patient] #list of possible passive roles

		self.outtype = outtype
		self.simplify = simplify

	def get_outtype(self):
		return self.outtype

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


	"""
	get_periphrastic_relations: output list of periphrastic properties
	"""
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

	def get_role(self,frame_occurrence,role_type="agentive"):
		assert role_type == "agentive" or role_type == "passive"
		if role_type == "agentive":
			agentive_roles = self.get_agentive_role(frame_occurrence)
			class_agentive_roles = list_map(self.graph.objects,agentive_roles,predicate=RDF.type)
			agentive_name = class_agentive_roles[0].split('#')[1]
			return agentive_roles, class_agentive_roles, agentive_name
		elif role_type == "passive":
			passive_roles = self.get_passive_role(frame_occurrence) #passive role associated to n-ary instance
			class_passive_roles = list_map(self.graph.objects,passive_roles,predicate=RDF.type) #TODO: can be made easier: maybe there is one passive role per n-ary relation?
			passive_name = class_passive_roles[0].split('#')[1] #name of the passive class
			return passive_roles, class_passive_roles, passive_name

	def get_roles(self,frame_occurrence):
		roles = []
		triples = self.graph.triples((frame_occurrence,None,None))
		for s,p,o in triples:
			if self.vn_data in p:
				class_role = list_map(self.graph.objects,[o],predicate=RDF.type)
				name = class_role[0].split('#')[1]
				roles.append([o,p,class_role,name])
		return roles

	"""
	add_labels: for each frodo object, add a label triple.
		    The label value is a string taken from the class/property name, which gets separated based on uppercase letters and turned into lowercase
	"""

	def add_labels(self):
		import re
		for s,p,o in self.graph.triples((None,None,None)):
			if self.frodo in s:
				label = s.rsplit('/',1)[1]
				label = ' '.join(re.findall('[a-zA-Z][^A-Z]*', label)) #splitting sentences based on uppercase letters
				self.graph.add((s,RDFS.label,Literal(label.lower())))

	"""
	apply_simplification: delete FRED's offsets
	"""

	def apply_simplification(self):
		def delete_offsets(self,offset):
			triples = self.graph.triples((offset,None,None))
			for s,p,o in list(triples):
				if p != self.semiotics.denotes and p != self.semiotics.hasInterpretant:
					delete_offsets(self,o)
				self.graph.remove((s,p,o))
				if len(list(self.graph.triples((None,p,None)))) == 0:
					self.graph.remove((p,None,None))

		offsets = list(self.graph.subjects(None,self.earmark.PointerRange))
		for el in offsets:
			delete_offsets(self,el)

	"""
	change_namespace: turn fred namespace to frodo
	"""

	def change_namespace(self):
		for s,p,o in self.graph.triples((None,None,None)):
			new_s, new_p, new_o = s,p,o
			if self.fred in s:
				new_s = URIRef(self.frodo+s.split('#')[1])
			if self.fred in p:
				new_p = URIRef(self.frodo+p.split('#')[1])
			if self.fred in o:
				new_o = URIRef(self.frodo+o.split('#')[1])
			self.graph.remove((s,p,o))
			self.graph.add((new_s,new_p,new_o))

	"""
	add_class_axioms: add type owl.Class triples for each class
	"""

	def add_class_axioms(self):
		for s,p,o in self.graph.triples((None,None,None)):
			if self.frodo in s and s.rsplit('/',1)[1][0].isupper(): #looking for classes
				self.graph.add((s,RDF.type,self.owl.Class))
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

			sub = self.graph.triples((superclass,None,None))
			obj = self.graph.triples((None,None,superclass))

			for s,p,o in sub:
				self.graph.add((URIRef(self.frodo+superclass_name),p,o))
			for s,p,o in obj:
				self.graph.add((s,p,URIRef(self.frodo+superclass_name)))

			self.graph.remove((superclass,None,None))
			self.graph.remove((None,None,superclass))

			#the code considers that there can be multiple roles, but only one role which is passive

			roles = self.get_roles(el)
			passive_found = -1
			for i in range(len(roles)):
				if roles[i][1] in self.passive:
					passive_found = i

			if passive_found == -1:
				if len(roles) != 0:
					passive_roles, pred_passive_role, class_passive_roles, passive_name = roles[0]
				if len(roles) > 1:
					agentive = roles[1:]
					#agentive_roles, pred_agentive_role, class_agentive_roles, agentive_name = roles[1]
			else:
				if len(roles) > 1:
					agentive = [x for i,x in enumerate(roles) if i != passive_found]
					#agentive_roles, pred_agentive_role, class_agentive_roles, agentive_name = roles[1-passive_found]

				if len(roles) != 0:
					passive_roles, pred_passive_role, class_passive_roles, passive_name = roles[passive_found]

					#add n-ary class
					self.graph.add((URIRef(self.frodo+passive_name+superclass_name),RDFS.subClassOf,URIRef(self.frodo+superclass_name)))

					#change type of n-ary instance
					self.graph.remove((el,RDF.type,None))
					self.graph.add((el,RDF.type,URIRef(self.frodo+passive_name+superclass_name)))

			if len(roles) != 0: #TODO: refactor
				self.graph.remove((el,pred_passive_role,None))
				self.graph.remove((pred_passive_role,None,self.owl.ObjectProperty))

				self.graph.add((URIRef(self.frodo+'involves{}'.format(passive_name)),RDF.type,self.owl.ObjectProperty))
				self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name)),RDF.type,self.owl.ObjectProperty))

				self.graph.add((URIRef(self.frodo+'involves{}'.format(passive_name)),RDFS.domain,self.owl.Thing))
				self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name)),RDFS.domain,class_passive_roles[0]))

				self.graph.add((URIRef(self.frodo+'involves{}'.format(passive_name)),RDFS.range,class_passive_roles[0]))
				self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name)),RDFS.range,self.owl.Thing))

				self.graph.add((URIRef(self.frodo+'involves{}'.format(passive_name)),self.owl.inverseOf,URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name))))
				self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name)),self.owl.inverseOf,URIRef(self.frodo+'involves{}'.format(passive_name))))

				self.graph.add((el,URIRef(self.frodo+'involves{}'.format(passive_name)),passive_roles))

				self.graph.add((passive_roles,URIRef(self.frodo+'is{}InvolvedIn'.format(passive_name)),el))

				blank_node2 = BNode()

				self.graph.add((blank_node2,RDF.type,self.owl.Restriction))
				self.graph.add((blank_node2,self.owl.onProperty,URIRef(self.frodo+'involves{}'.format(passive_name))))
				self.graph.add((blank_node2,self.owl.someValuesFrom, URIRef(self.frodo+'involves{}'.format(passive_name))))

				if passive_found == -1:
					self.graph.add((URIRef(self.frodo+superclass_name),RDFS.subClassOf,blank_node2))
				else:
					self.graph.add((URIRef(self.frodo+passive_name+superclass_name),RDFS.subClassOf,blank_node2))

			if len(roles) > 1:
				for agentive_roles, pred_agentive_role, class_agentive_roles, agentive_name in agentive:
					#change property names
					self.graph.remove((el,pred_agentive_role,None))
					self.graph.remove((pred_agentive_role,None,self.owl.ObjectProperty))

					self.graph.add((URIRef(self.frodo+'involves{}'.format(agentive_name)),RDF.type,self.owl.ObjectProperty)) #setting new relations as properties
					self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)),RDF.type,self.owl.ObjectProperty))

					self.graph.add((URIRef(self.frodo+'involves{}'.format(agentive_name)),RDFS.domain,self.owl.Thing)) #setting domain axioms to properties
					self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)),RDFS.domain,class_agentive_roles[0]))

					self.graph.add((URIRef(self.frodo+'involves{}'.format(agentive_name)),RDFS.range,class_agentive_roles[0])) #setting range axioms to properties
					self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)),RDFS.range,self.owl.Thing))

					self.graph.add((URIRef(self.frodo+'involves{}'.format(agentive_name)),self.owl.inverseOf,URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)))) #setting inverseOf relations
					self.graph.add((URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)),self.owl.inverseOf,URIRef(self.frodo+'involves{}'.format(agentive_name))))

					self.graph.add((el,URIRef(self.frodo+'involves{}'.format(agentive_name)),agentive_roles)) #setting newly created properties between class instances

					self.graph.add((agentive_roles,URIRef(self.frodo+'is{}InvolvedIn'.format(agentive_name)),el))

					#adding subclass restrictions to newly created class
					blank_node1 = BNode()

					self.graph.add((blank_node1,RDF.type,self.owl.Restriction))
					self.graph.add((blank_node1,self.owl.onProperty,URIRef(self.frodo+'involves{}'.format(agentive_name))))
					self.graph.add((blank_node1,self.owl.someValuesFrom, URIRef(self.frodo+'involves{}'.format(agentive_name)))) #someValuesFrom and allValuesFrom should be the same, given the range axioms of the properties

					if passive_found == -1:
						self.graph.add((URIRef(self.frodo+superclass_name),RDFS.subClassOf,blank_node1))
					else:
						self.graph.add((URIRef(self.frodo+passive_name+superclass_name),RDFS.subClassOf,blank_node1))

			#self.change_agentive_passive_namespace(el)
			self.add_labels()

		if self.simplify:
			self.apply_simplification()
		self.change_namespace()
		self.add_class_axioms()


	def change_periphrastic_property_name(self,properties):
		for prop in properties:
			pred = list(self.graph.triples((None,prop,None)))

			for triple in pred:
				passive_class = list(self.graph.triples((triple[2],RDF.type,None)))[0][2]
				new_pred_name = self.frodo+triple[1].split('#')[1]+passive_class.split('#')[1]
				splitted_new_pred_name = new_pred_name.rsplit('/',1)
				splitted_new_pred_name[1] = splitted_new_pred_name[1][0].upper()+splitted_new_pred_name[1][1:]
				new_pred_name = URIRef(new_pred_name)
				inverse_pred_name = URIRef(splitted_new_pred_name[0]+"/is{}Of".format(splitted_new_pred_name[1]))

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
		try:
			for el in rdf:
				self.graph.parse(data=el, format="application/rdf+xml")
				self.periphrastic_parsing()
				self.n_ary_parsing()
			return self.graph.serialize(format=self.outtype)
		except e:
			print(e)
			print("Error: FRODO is not able to produce an output")
			return None
