from fred import fred

fr = fred()
rdf = fr.get_rdf('the cat is on the table')

print(rdf)
