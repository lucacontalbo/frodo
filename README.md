# FRODO

This is a re-implementation of FRODO (https://arxiv.org/pdf/2206.02485.pdf). This is not the **official** implementation, thus all correlated Web API don't use this version.

What's more? This command line tool integrates Raptor/Graphviz to allow the users to create ontology diagrams directly from the output, in any format allowed by Graphviz.

The main program is launched from *frodo.py*. For info about its usage, look at the help command.

## Dependecies

The program is **not guaranteed** to work with versions different than the followings:

- python3
- dot - graphviz: 2.43.0
- rapper: 2.0.15

## How is FRED queried?

FRED can be queried automatically with the -a flag. For that to work, you have to follow the given instructions in https://www.semantic-web-journal.net/system/files/swj1007.pdf. The obtained token **must** be places in the same dir where *frodo.py* is. In case the command does not work because the API cannot be reached, you can obtain the ontology by querying http://semantics.istc.cnr.it/fred and copy paste the result in a file inside the saved_rdfs dir. The filename **must** be called like the competency question without spaces and without the file format.