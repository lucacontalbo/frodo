from subprocess import check_output
import subprocess
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class Rdf2Graph:
	def __init__(self):
		pass

	def get_png(self,rdf,from_format='xml',to_format='png',file_name=''):
		rdf = rdf.split()
		rdf = '+'.join(rdf)
		if file_name != '':
			file_name = "graph_png/"+file_name
			#file_name += ".{}".format(to_format)
			subprocess.Popen("wget 'http://www.ldf.fi/service/rdf-grapher?rdf={}&from={}&to={}' -O {}".format(rdf,from_format,to_format,file_name),shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")
			print("http://www.ldf.fi/service/rdf-grapher?rdf={}&from={}&to={}".format(rdf,from_format,to_format))
			self.visualize(file_name)
		else: #result won't be saved
			file_name = "tmp.png"
			subprocess.Popen("wget 'http://www.ldf.fi/service/rdf-grapher?rdf={}&from={}&to={}' -O {}".format(rdf,from_format,to_format,"tmp"),shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")
			self.visualize(file_name)
			os.remove(file_name)

	def visualize(self,file_name):
		"""print(file_name)
		img = mpimg.imread(file_name)
		plt.imshow(img)
		plt.show()"""
		from PIL import Image

		image = Image.open(file_name)
		image.show()
