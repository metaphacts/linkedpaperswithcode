import rdflib
from rdflib import Graph, URIRef
import numpy as np

#create a rdflib graph object
graph = rdflib.Graph()

#path to the linkedpaperswithcode.nt file
file_path = ".../linkedpaperswithcode.nt"

#load the file into the graph object
graph.parse(file_path, format="nt")

#list of all classes
class_list = [
    URIRef("https://linkedpaperswithcode.com/class/task"),
    URIRef("https://linkedpaperswithcode.com/class/dataset"),
    URIRef("https://linkedpaperswithcode.com/class/paper"),
    URIRef("https://linkedpaperswithcode.com/class/method"),
    URIRef("https://linkedpaperswithcode.com/class/category"),
    URIRef("https://linkedpaperswithcode.com/class/area"),
    URIRef("https://linkedpaperswithcode.com/class/conference"),
    URIRef("https://linkedpaperswithcode.com/class/evaluation"),
    URIRef("https://linkedpaperswithcode.com/class/model"),
    URIRef("https://linkedpaperswithcode.com/class/dataloader"),
    URIRef("https://linkedpaperswithcode.com/class/repository")

]

#List of all predicates
pred_list = [
    URIRef("https://linkedpaperswithcode.com/property/hasTask"),    
    URIRef("https://linkedpaperswithcode.com/property/usedForTask"),
    URIRef("https://dbpedia.org/property/area"),
    URIRef("https://linkedpaperswithcode.com/property/mainCategory"),
    URIRef("https://dbpedia.org/property/category"),
    URIRef("https://linkedpaperswithcode.com/property/hasMethod"), 
    URIRef("https://linkedpaperswithcode.com/property/introducedBy"),
    URIRef("https://linkedpaperswithcode.com/property/hasConference"),
    URIRef("https://linkedpaperswithcode.com/property/hasEvaluation"),
    URIRef("https://linkedpaperswithcode.com/property/hasDataset"),
    URIRef("https://linkedpaperswithcode.com/property/hasModel"), 
    URIRef("https://linkedpaperswithcode.com/property/hasDataLoader"),
    URIRef("https://linkedpaperswithcode.com/property/hasRepository"),
    URIRef("https://linkedpaperswithcode.com/property/hasOfficialRepository"),
    URIRef("https://linkedpaperswithcode.com/property/usesDataset")
]


#initialise the entity and relation counter
entity_counter = 0
relation_counter = 0
entity_dict = {}
relation_dict = {}

triples = []

#iterate over all triples in the graph
for s, p, o in graph:

    if p == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
        if o not in class_list:
            continue
    else:
        o_classes = [obj for obj in graph.objects(o, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))]
        s_classes = [obj for obj in graph.objects(s, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))]

        #skip if the object or the subject are not a class in the class list
        if type(o) is URIRef and not any(oc in class_list for oc in o_classes):
            continue
        if type(s) is URIRef and not any(sc in class_list for sc in s_classes):
            continue

    #skip literals and predicates that are not in the predicate list
    if type(o) is not URIRef or p not in pred_list:
        continue

    #check if subject and object are in the entity dictionary, if not add them
    if s not in entity_dict and s not in class_list:
        entity_dict[s] = entity_counter
        entity_counter += 1

    if o not in entity_dict and o not in class_list:
        entity_dict[o] = entity_counter
        entity_counter += 1

    if p not in relation_dict:
        relation_dict[p] = relation_counter
        relation_counter += 1

    #check if subject, predicate and object are in the mapping before adding the triple
    if s in entity_dict and p in relation_dict and o in entity_dict:
        triples.append((entity_dict[s], relation_dict[p], entity_dict[o]))


#save the numeric triples in a text file
np.savetxt('.../triples_input_embeddings.txt', triples, fmt='%i')

#save the entity and relation mapping in a text file
with open('.../entity_mapping.txt', 'w') as f:
    for key, value in entity_dict.items():
        f.write('%s\t%i\n' % (str(key), value))

with open('.../relation_mapping.txt', 'w') as f:
    for key, value in relation_dict.items():
        f.write('%s\t%i\n' % (str(key), value))


print("Done preprocessing linkedpaperswithcode knowledge graph for input for embeddings")