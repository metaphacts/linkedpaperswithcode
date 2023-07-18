'''
Load all created .nt files from the transformation scripts (01_papers.py, 02_conferences.py,
03_methods.py, 04_papers-code-and-datasets.py and 05_evaluation-tables.py) and entity linking 
scripts (01_link_authors.py, 02_link_papers.py, 03_link_areas.py and 04_link_datasets.py) into
an rdflib graph.
It is then serialized into a single N-Triples file (linkedpaperswithcode.nt) 
and a single turtle file (linkedpaperswithcode.ttl).

Output: finale linkedpaperswithcode RDF Dumps (linkedpaperswithcode.nt and linkedpaperswithcode.ttl)
'''

from rdflib import Graph

g = Graph()


#Liste of all .nt files
files = [".../papers.nt", ".../conferences.nt", ".../methods.nt", ".../papers_code.nt", ".../datasets.nt", 
         ".../evaluation-tables.nt", ".../author-links.nt", ".../paper-links.nt", ".../area-links.nt", ".../dataset-links.nt"]

for file in files:
    g.parse(file, format="nt")


#serialize graph into a single N-Triples file and a single turtle file
g.serialize(destination='.../linkedpaperswithcode.nt', format='nt')
print("Created N-Triples file")

g.serialize(destination='.../linkedpaperswithcode.ttl', format='turtle')
print("Created Turtle file")

print("Done")