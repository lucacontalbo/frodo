from fred import Fred
from parser import Parser
from tester import Tester

fred = Fred()
parser = Parser()

#tester = Tester(fred,parser)
#tester.test()
rdf = fred.get_rdf(['Who commissioned the component of a system?'])
parser.parse(rdf)
