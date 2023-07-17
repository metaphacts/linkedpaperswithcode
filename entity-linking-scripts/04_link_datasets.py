#link linkedpaperswithcode datasets to Wikidata Datasets (wdt:P31/wdt:P279* wd:Q1172284)
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import time
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON

#Path to datasets.json input file
file_path = ".../datasets.json"

#Path to area-links.nt output file (containing owl:sameAs triples)
ntriple_output_file_path = ".../datasets-links.nt"

#Path to the output file containing the summary of the linking process
summary_output_file_path = ".../datasets-links-summary.txt"


start_time = time.ctime()
print('linking datasets to Wikidata works started at: '+ start_time)

#Info for namespaces used in LinkedPapersWithCode
lpwc_namespace = "https://linkedpaperswithcode.org"
lpwc_namespace_class = "https://linkedpaperswithcode.org/class"

lpwc_dataset_class = URIRef(lpwc_namespace_class + "/dataset")

#LinkedPapersWithCode classes used in this file
lpwc_dataset = URIRef(lpwc_namespace + "/dataset/")

lpwc_graph = Graph()

query_dataset = """ 
    SELECT DISTINCT ?item WHERE {
    VALUES ?name { "?DATASET_NAME"@en "?DATASET_NAME"@de "?DATASET_NAME"@fr "?DATASET_NAME"@it }
    ?item wdt:P31/wdt:P279* wd:Q1172284;
        rdfs:label ?name.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de,fr,it". }
    }
    LIMIT 1
"""

query_dataset_full_name = """ 
    SELECT DISTINCT ?item WHERE {
    VALUES ?name { "?DATASET_NAME"@en "?DATASET_FULL_NAME"@en "?DATASET_NAME"@de "?DATASET_FULL_NAME"@de "?DATASET_NAME"@fr "?DATASET_FULL_NAME"@fr "?DATASET_NAME"@it "?DATASET_FULL_NAME"@it}
    {
        ?item wdt:P31/wdt:P279* wd:Q1172284;
            rdfs:label ?name.
    } UNION {
        ?item wdt:P31/wdt:P279* wd:Q1172284;
            skos:altLabel ?name.
    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de,fr,it". }
    }
    LIMIT 1
"""

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


i = 0
datasets_linked_count = 0
datasets_not_linked_count = 0
with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    # JSON-Datei öffnen und als Liste von Objekten laden
    with open(file_path, 'r') as file:
        datasets = json.load(file)

        for dataset in datasets:

            #paper-id
            dataset_id = dataset["url"].replace("https://paperswithcode.com/dataset/", "")
            dataset_uri = URIRef(lpwc_dataset + dataset_id)
           
            #link datasets to wikidata
            dataset_name = dataset["name"]
            if dataset["full_name"] != "":
                dataset_full_name = dataset["full_name"]
                query_replace = query_dataset_full_name.replace("?DATASET_NAME", f"{dataset_name}").replace("?DATASET_FULL_NAME", f"{dataset_full_name}")
            else:
                query_replace = query_dataset.replace("?DATASET_NAME", f"{dataset_name}")

            sparql.setQuery(query_replace)
            sparql.setReturnFormat(JSON)
            try:

                results = sparql.query().convert()

                if results["results"]["bindings"]:
                    wikidata_dataset_uri = results["results"]["bindings"][0]["item"]["value"]
                    lpwc_graph.add((dataset_uri, OWL.sameAs, URIRef(wikidata_dataset_uri)))
                    datasets_linked_count += 1
                else:
                    datasets_not_linked_count += 1
            except:
                datasets_not_linked_count += 1


            i += 1

            if i % 100 == 0:
                print('Linked {} Dataset entities to Wikidata Datasets'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        # Write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()  

end_time = time.ctime()
with open(summary_output_file_path, "w",) as z:
    z.write('Start Time: {} .\n'.format(start_time))
    z.write('Items (lines) processed: {} .\n'.format(i))
    z.write('Datasets linked to Wikidata: {} .\n'.format(datasets_linked_count))
    z.write('Datasets not linked to Wikidata: {} .\n'.format(datasets_not_linked_count))
    z.write('End Time: {} .\n'.format(end_time))
    z.close()

print("Done") 
