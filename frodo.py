from fred import Fred
from parser import Parser
from tester import Tester
import argparse


argparser = argparse.ArgumentParser(prog="python3 frodo.py", description="Implementation of FRODO parser, relying on FRED's rdfs and Raptor/Graphviz for visualization")
argparser.add_argument("-c","--competency-question", action="store",help="Competency question translated by FRODO", required=True)
argparser.add_argument("-o","--outtype",help="RDF output syntax [xml,ttl,nt]. Default: xml",action="store",default="xml")
argparser.add_argument("-s","--save",help="Save graph representation to view_graph/{OUTPUT_FILE}. The accepted file formats are [dot,xdot,ps,pdf,svg,fig,png,gif,jpg,jpeg,json,imap,cmapx].\n Without this flag, FRODO only prints the associated FRODO ontology",action="store",default='')
argparser.add_argument("-S","--simplify",help="Outputs ontology without meta-information given by FRED",action="store_true")
argparser.add_argument("-a","--auto",action="store_true",help="Get FRED's ontology automatically from its API")

args = argparser.parse_args()
competency_question, outtype, save, simplify, auto = args.competency_question, args.outtype, args.save, args.simplify, args.auto

allowed_outtype = ["xml","ttl","nt"]
allowed_save_formats = ["dot","xdot","ps","pdf","svg","fig","png","gif","jpg","jpeg","json","imap","cmapx"]

splitted_save = save.split('.')

if outtype not in allowed_outtype:
	print("ArgumentError: -o/--outtype must be one between xml,ttl,nt")
elif save != '' and len(splitted_save) <= 1:
	print("ArgumentError: -s/--save please add the file extension")
elif save != '' and splitted_save[1] not in allowed_save_formats:
	print("ArgumentError: -s/--save extension is not allowed")
else:
	fred = Fred(auto)
	parser = Parser(outtype,simplify)

	tester = Tester(fred,parser,competency_question,save)
	tester.test()
