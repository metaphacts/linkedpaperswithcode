#link linkedpaperswithcode areas to SemOpenAlex Concepts
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import nltk
import time
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

#Path to area-links.nt output file (containing owl:sameAs triples)
ntriple_output_file_path = ".../area-links.nt"

#Path to the output file containing the summary of the linking process
summary_output_file_path = ".../area-links-summary.txt"


def transform_title_to_lowercase(title):
    lower_title = title.lower()
    transformed_title = lower_title.capitalize()
    return transformed_title

def transform_title_to_capitalize_case(title):
    words = title.split()
    transformed_words = [word.capitalize() if word.lower() not in stop_words else word.lower() for word in words]
    transformed_title = ' '.join(transformed_words)
    return transformed_title

start_time = time.ctime()
print('linking areas to SemOpenAlex concepts started at: '+ start_time)

lpwc_graph = Graph()

#areas via api
from paperswithcode import PapersWithCodeClient 

client = PapersWithCodeClient()

def get_all_areas(client):
    page = 1 
    all_areas = []

    while True:
        areas = client.area_list(page=page)
        all_areas.extend(areas.results)

        if areas.next_page is None:  
            break

        page = areas.next_page 

    return all_areas


area_list = get_all_areas(client)

query_area = """ 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX soa: <https://semopenalex.org/ontology/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT DISTINCT ?concept WHERE {
    ?concept rdf:type skos:Concept .
    { ?concept skos:prefLabel "?CONCEPT_TITLE"^^xsd:string . }
    UNION
    { ?concept skos:prefLabel "?LOWERCASE"^^xsd:string . }
    UNION
    { ?concept skos:prefLabel "?CAPITALIZE_CASE"^^xsd:string . }
    }
    LIMIT 1
"""
sparql = SPARQLWrapper("https://semopenalex.org/sparql")


i = 0
concepts_linked_count = 0
concepts_not_linked_count = 0

for area in area_list:
    area_id = area.id
    area_name = area.name
    area_uri = "https://linkedpaperswithcode.com/area/" + area_id
    area_uri = URIRef(area_uri)
    area_name_lowercase = transform_title_to_lowercase(area_name)
    area_name_capitalize_case = transform_title_to_capitalize_case(area_name)
    query_replace = query_area.replace("?CONCEPT_TITLE", f"{area_name}").replace("?LOWERCASE", f"{area_name_lowercase}").replace("?CAPITALIZE_CASE", f"{area_name_capitalize_case}")
    sparql.setQuery(query_replace)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            soa_concept_uri = results["results"]["bindings"][0]["concept"]["value"]
            lpwc_graph.add((area_uri, OWL.sameAs, URIRef(soa_concept_uri)))
            concepts_linked_count += 1
        else:
            concepts_not_linked_count += 1
    except:
        concepts_not_linked_count += 1

    i += 1


with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    g.write(lpwc_graph.serialize(format='nt'))


g.close()  

end_time = time.ctime()
with open(summary_output_file_path, "w",) as z:
    z.write('Start Time: {} .\n'.format(start_time))
    z.write('Items (lines) processed: {} .\n'.format(i))
    z.write('Areas linked to SemOpenAlex: {} .\n'.format(concepts_linked_count))
    z.write('Areas not linked to SemOpenAlex: {} .\n'.format(concepts_not_linked_count))
    z.write('End Time: {} .\n'.format(end_time))
    z.close()

print("Done") 
