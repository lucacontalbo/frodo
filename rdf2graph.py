from subprocess import check_output
import subprocess
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class Rdf2Graph:
	"""
	SAVE: boolean value indicating whether to save the file produced by graphviz
	"""
	def __init__(self,save_path):
		self.save_path = save_path
		self.format2format = { #maps rapper formats to graphviz formats
			"xml": "rdfxml",
			"nt": "ntriples",
			"ttl": "turtle"
		}

	def get_save_path(self):
		return self.save_path

	"""
	This function uses rapper (Raptor) and Graphviz utility to visualize the graph,
	by translating the rdf to dot notation and then visualizing it.

	rdf: rdf graph as string
	from_format: rapper input format
	to_format: graphviz output format
	filename: filename used to save the file
	"""

	def visualize(self,rdf,from_format="rdf"):
		splitted_save_path = self.save_path.split('.')
		file_name, to_format = splitted_save_path[0], splitted_save_path[1]

		rapper_input_format = self.format2format[from_format]
		with open("tmp.{}".format(from_format),'w') as f:
			f.write(rdf)
		subprocess.Popen("rapper -i {} -o dot tmp.{} > tmp.dot".format(rapper_input_format,from_format),shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")
		subprocess.Popen("dot -T{0} tmp.dot > view_graph/{1}.{0}".format(to_format,file_name),shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")
		print("Created file view_graph/{}.{}".format(file_name,to_format))
		#subprocess.Popen("evince view_graph/{}.{}".format(file_name,to_format),shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")

		os.remove("tmp.{}".format(from_format))
		os.remove("tmp.dot")
