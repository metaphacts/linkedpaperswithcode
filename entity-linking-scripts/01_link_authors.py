#link paperswithcode author name strings to author entities in SemOpenAlex
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import time
import jellyfish
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

#Path to papers.json input file
file_path = '.../papers.json'

#Path to author-links.nt output file (containing owl:sameAs and lpwc:creatorName triples)
ntriple_output_file_path = ".../author-links.nt"

#Path to the output file containing the summary of the linking process
summary_output_file_path = ".../author-links-summary.txt"


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
print('linking author strings to SemOpenAlex entity started at: '+ start_time)


#Info for namespaces, classes and properties used in LinkedPapersWithCode
lpwc_namespace = "https://linkedpaperswithcode.com"
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
creator_name = URIRef("https://linkedpaperswithcode.com/property/creatorName")

lpwc_graph = Graph()

query_authors_a = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX soa: <https://semopenalex.org/ontology/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?author WHERE {
    ?paper rdf:type <https://semopenalex.org/ontology/Work> .
    ?author rdf:type <https://semopenalex.org/ontology/Author> .
    ?paper dcterms:title ?paperTitle . 
    ?paper dcterms:creator ?author . 
    ?author foaf:name "?AUTHOR_NAME"^^xsd:string .
    FILTER(CONTAINS(LCASE(?paperTitle), "?PAPER_TITLE"^^xsd:string))
    ?author soa:worksCount ?worksCount . 
    } 
    ORDER BY DESC (?worksCount)
    LIMIT 1
"""

query_authors_b = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX soa: <https://semopenalex.org/ontology/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?author ?authorName WHERE {
    ?paper rdf:type <https://semopenalex.org/ontology/Work> .
    ?author rdf:type <https://semopenalex.org/ontology/Author> .
    { ?paper dcterms:title "?PAPER_TITLE"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?DOT"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?LOWERCASE"^^xsd:string . }
    UNION
    { ?paper dcterms:title "?CAPITALIZE_CASE"^^xsd:string . }
    ?paper dcterms:creator ?author . 
    ?author foaf:name ?authorName .
    } 
"""

sparql = SPARQLWrapper("https://semopenalex.org/sparql")


i = 0
author_count = 0
author_linked_count = 0
author_not_linked_count = 0
authors_linked_query_a = 0
authors_linked_query_b = 0
with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    # JSON-Datei öffnen und als Liste von Objekten laden
    with open(file_path, 'r') as file:
        papers = json.load(file)

        for paper in papers:

            #paper-id
            paper_id = paper["paper_url"].replace("https://paperswithcode.com/paper/", "")
            paper_uri = URIRef(lpwc_paper + paper_id)

            #authors
            if paper["authors"] != []:
                for author in paper["authors"]:
                    author_count += 1
                    paper_title_lower = paper["title"].lower()
                    query_replace = query_authors_a.replace("?AUTHOR_NAME", f"{author}").replace("?PAPER_TITLE", f"{paper_title_lower}")
                    sparql.setQuery(query_replace)
                    sparql.setReturnFormat(JSON)

                    try:
                        results = sparql.query().convert()
                        if results["results"]["bindings"]:
                            soa_author_uri = results["results"]["bindings"][0]["author"]["value"]
                            lpwc_graph.add((paper_uri, DCTERMS.creator, URIRef(soa_author_uri)))
                            authors_linked_query_a += 1
                            author_linked_count += 1

                        else:
                            paper_title = paper["title"]
                            paper_title_dot = paper_title + "."
                            paper_title_lowercase = transform_title_to_lowercase(paper_title)
                            paper_title_capitalize_case = transform_title_to_capitalize_case(paper_title)
                            query_replace = query_authors_b.replace("?PAPER_TITLE", f"{paper_title}").replace("?DOT", f"{paper_title_dot}").replace("?LOWERCASE", f"{paper_title_lowercase}").replace("?CAPITALIZE_CASE", f"{paper_title_capitalize_case}")
                            sparql.setQuery(query_replace)
                            sparql.setReturnFormat(JSON)
                            results = sparql.query().convert()
                            data = results["results"]["bindings"]
                            if data:
                                author_found = False
                                for row in data:
                                    author_name = row["authorName"]["value"]
                                    jw_distance = jellyfish.jaro_winkler(author, author_name)
                                    if jw_distance > 0.9:
                                        soa_author_uri = row["author"]["value"]
                                        lpwc_graph.add((paper_uri, DCTERMS.creator, URIRef(soa_author_uri)))
                                        authors_linked_query_b += 1
                                        author_linked_count += 1
                                        author_found = True
                                        break
                                if not author_found:
                                    lpwc_graph.add((paper_uri, creator_name, Literal(author, datatype=XSD.string)))
                                    author_not_linked_count += 1



                            else:
                                lpwc_graph.add((paper_uri, creator_name, Literal(author, datatype=XSD.string)))
                                author_not_linked_count += 1



                    except:
                        lpwc_graph.add((paper_uri, creator_name, Literal(author, datatype=XSD.string)))
                        author_not_linked_count += 1



            i += 1
            if i % 200 == 0:
                print('Linked the Authors of {} Paper entities to SemOpenAlex'.format(i))

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
   #z.write('Errors encountered: {} .\n'.format(error_count))
    z.write('Authors processed: {} .\n'.format(author_count))
    z.write('Authors linked to SemOpenAlex: {} .\n'.format(author_linked_count))
    z.write('Authors not linked to SemOpenAlex: {} .\n'.format(author_not_linked_count))
    z.write('Authors linked with query a: {} .\n'.format(authors_linked_query_a))
    z.write('Authors linked with query b: {} .\n'.format(authors_linked_query_b))
    z.write('End Time: {} .\n'.format(end_time))
    z.close()

print("Done") 
