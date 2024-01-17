#link linkedpaperswithcode papers to SemOpenAlex Works
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal, Namespace, RDF, OWL
import time
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

#Path to papers.json input file
file_path = '.../papers.json'

#Path to paper-links.nt output file (containing owl:sameAs triples)
ntriple_output_file_path = ".../paper-links.nt"

#Path to the output file containing the summary of the linking process
summary_output_file_path = ".../paper-links-summary.txt"


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
print('linking papers to SemOpenAlex works started at: '+ start_time)


lpwc_graph = Graph()
lpwc_namespace = "https://linkedpaperswithcode.com"
lpwc_paper = URIRef(lpwc_namespace + "/paper/")


query_work = """ 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX soa: <https://semopenalex.org/ontology/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?paper WHERE {
    ?paper rdf:type <https://semopenalex.org/ontology/Work> .
    { ?paper dcterms:title "?PAPER_TITLE"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?DOT"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?LOWERCASE"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?CAPITALIZE_CASE"^^xsd:string . }
    ?paper soa:citedByCount ?citedByCount .
    } 
    ORDER BY DESC(?citedByCount)
    LIMIT 1
"""

sparql = SPARQLWrapper("https://semopenalex.org/sparql")


i = 0
papers_linked_count = 0
papers_not_linked_count = 0
with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    # JSON-Datei öffnen und als Liste von Objekten laden
    with open(file_path, 'r') as file:
        papers = json.load(file)

        for paper in papers:

            #paper-id
            paper_id = paper["paper_url"].replace("https://paperswithcode.com/paper/", "")
            paper_uri = URIRef(lpwc_paper + paper_id)
           
            if paper["title"] != "" and paper["title"] is not None: 
                #link papers to SemOpenAlex Works
                paper_title = paper["title"]
                paper_title_dot = paper_title + "."
                paper_title_lowercase = transform_title_to_lowercase(paper_title)
                paper_title_capitalize_case = transform_title_to_capitalize_case(paper_title)
                query_replace = query_work.replace("?PAPER_TITLE", f"{paper_title}").replace("?DOT", f"{paper_title_dot}").replace("?LOWERCASE", f"{paper_title_lowercase}").replace("?CAPITALIZE_CASE", f"{paper_title_capitalize_case}")
                sparql.setQuery(query_replace)
                sparql.setReturnFormat(JSON)
                try:
                    results = sparql.query().convert()
                    if results["results"]["bindings"]:
                        soa_work_uri = results["results"]["bindings"][0]["paper"]["value"]
                        lpwc_graph.add((paper_uri, OWL.sameAs, URIRef(soa_work_uri)))
                        papers_linked_count += 1
                    else:
                        papers_not_linked_count += 1
                except:
                    papers_not_linked_count += 1


            i += 1
            if i % 200 == 0:
                print('Linked {} Paper entities to SemOpenAlex Works'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        #write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()  

end_time = time.ctime()
with open(summary_output_file_path, "w",) as z:
    z.write('Start Time: {} .\n'.format(start_time))
    z.write('Items (lines) processed: {} .\n'.format(i))
    z.write('Papers with title linked to SemOpenAlex: {} .\n'.format(papers_linked_count))
    z.write('Papers with title not linked to SemOpenAlex: {} .\n'.format(papers_not_linked_count))
    z.write('End Time: {} .\n'.format(end_time))
    z.close()

print("Done") 
