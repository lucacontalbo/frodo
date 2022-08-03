from fred import fred
from parser import parser

fr = fred()
rdf = fr.get_rdf('Who commissioned a component of a system?')

parser = parser()
parser.parse(rdf)
