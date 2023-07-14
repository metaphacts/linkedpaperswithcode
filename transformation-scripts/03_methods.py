"""
    Input files: 
        methods.json
    Output file:
        methods.nt
"""

from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import json
import re
import html2text
import markdown

#Path to methods.json input file
file_path = '.../methods.json'

#Path to methods.nt output file
ntriple_output_file_path = ".../methods.nt"


replacements = [
    {
        "search": re.compile(r'"'),
        "replace": '',  # &quot;
        "comment": "Unescaped quotation marks"
    }, {
        "search": re.compile(r'\\'),
        "replace": '',  # &#92;
        "comment": "Unescaped backslash"
    }, {
        "search": re.compile(r'\n'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\b'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\t'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\r'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\f'),
        "replace": '',
        "comment": "Newline string"
    }
]
replacements_url = [
    {
        "search": re.compile(r'"'),
        "replace": '%22',
        "comment": "Unescaped quotation mark in URI"
    }, {
        "search": re.compile(r'\\'),
        "replace": '%5c',
        "comment": "Unescaped backslash in URI"
    }, {
        "search": re.compile(r'\n'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\r'),
        "replace": '',
        "comment": "Newline string"
    }, {
        "search": re.compile(r'\t'),
        "replace": '',
        "comment": "Newline string"
    },
]


def clean(nameStr):
    cleaned_str = nameStr
    for r in replacements:
        if re.search(r["search"], nameStr):
            cleaned_str = re.sub(r["search"], r["replace"], cleaned_str)
    return cleaned_str


def clean_url(nameStr):
    cleaned_str = nameStr
    for r in replacements_url:
        if re.search(r["search"], nameStr):
            cleaned_str = re.sub(r["search"], r["replace"], cleaned_str)
    return cleaned_str


def convert_markdown_to_plain_text(md_string):
    html = markdown.markdown(md_string)
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.ignore_emphasis = True
    plain_text = text_maker.handle(html)
    return plain_text


#Info for namespaces used in LinkedPapersWithCode
lpwc_namespace = "https://linkedpaperswithcode.com"
lpwc_namespace_class = "https://linkedpaperswithcode.com/class"

lpwc_paper_class = URIRef(lpwc_namespace_class + "/paper")
lpwc_task_class = URIRef(lpwc_namespace_class + "/task")
lpwc_venue_class = URIRef(lpwc_namespace_class + "/venue")
lpwc_method_class = URIRef(lpwc_namespace_class + "/method")
lpwc_category_class = URIRef(lpwc_namespace_class + "/category")
lpwc_area_class = URIRef(lpwc_namespace_class + "/area")

#LinkedPapersWithCode classes used in this file
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
lpwc_task = URIRef(lpwc_namespace + "/task/")
lpwc_venue = URIRef(lpwc_namespace + "/venue/")
lpwc_method = URIRef(lpwc_namespace + "/method/")
lpwc_category = URIRef(lpwc_namespace + "/methods/category/")
lpwc_area = URIRef(lpwc_namespace + "/area/")

#LinkedPapersWithCode predicates used in this file
has_full_name = URIRef("https://dbpedia.org/property/fullname")
introduced_by = URIRef("https://linkedpaperswithcode.com/property/introducedBy")
introduced_year = URIRef("https://linkedpaperswithcode.com/property/introducedYear")
has_code_snippet = URIRef("https://linkedpaperswithcode.com/property/codeSnippet")
has_number_papers = URIRef("https://linkedpaperswithcode.com/property/numberPapers")
has_category = URIRef("https://dbpedia.org/property/category")
has_area  = URIRef("https://dbpedia.org/property/area")


lpwc_graph = Graph()
area_mapping = {}

i = 0
with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    with open(file_path, 'r') as file:
        methods = json.load(file)
        for method in methods:

            #method-id
            method_id = method["url"].replace("https://paperswithcode.com/method/", "")
            method_uri = URIRef(lpwc_method + method_id)
            lpwc_graph.add((method_uri, RDF.type, lpwc_method_class))

            #name
            method_title = clean(method["name"])
            lpwc_graph.add((method_uri, FOAF.name , Literal(method_title, datatype=XSD.string)))

            #full_name
            if method["full_name"] != None:
                method_full_name = clean(method["full_name"])
                lpwc_graph.add((method_uri, has_full_name , Literal(method_full_name, datatype=XSD.string)))

            #description
            if method["description"] != "":
                method_description = convert_markdown_to_plain_text(method["description"])
                method_description = clean(method_description)
                lpwc_graph.add((method_uri, DCTERMS.description, Literal(method_description, datatype=XSD.string)))

            #paper
            if method["paper"] != None:
                paper_id = method["paper"]["url"].replace("https://paperswithcode.com/paper/", "")
                paper_uri = URIRef(lpwc_paper + paper_id)
                lpwc_graph.add((method_uri, introduced_by, paper_uri))

            #introduced_year
            if method["introduced_year"] != None:
                method_introduced_year = method["introduced_year"]
                lpwc_graph.add((method_uri, introduced_year, Literal(method_introduced_year, datatype=XSD.gYear)))
            
            #source_url
            if method["source_url"] != None:
                method_source_url = clean_url(method["source_url"])
                lpwc_graph.add((method_uri, DCTERMS.source, Literal(method_source_url, datatype=XSD.anyURI)))

            #code_snippet_url
            if method["code_snippet_url"] != None and method["code_snippet_url"] != "":
                method_code_snippet_url = clean_url(method["code_snippet_url"])
                lpwc_graph.add((method_uri, has_code_snippet, Literal(method_code_snippet_url, datatype=XSD.anyURI)))

            #num_papers
            if method["num_papers"] != None:
                method_num_papers = method["num_papers"]
                lpwc_graph.add((method_uri, has_number_papers, Literal(method_num_papers, datatype=XSD.integer)))
            
            #collections und area als eigene Klassen
            if method["collections"] != None:
                for collection in method["collections"]:
                    collection_id = collection["collection"].replace(" ", "-").lower()
                    collection_id = clean_url(collection_id)
                    collection_uri = URIRef(lpwc_category + collection_id)
                    collection_name = clean(collection["collection"])
                    lpwc_graph.add((collection_uri, RDF.type, lpwc_category_class))
                    lpwc_graph.add((collection_uri, FOAF.name, Literal(collection_name, datatype=XSD.string)))
                    lpwc_graph.add((method_uri, has_category, collection_uri))

                    #area
                    if collection["area"] not in area_mapping:
                        area_id = collection["area_id"]
                        area_id = clean_url(area_id)
                        area_uri = URIRef(lpwc_area + area_id)
                        area_name = clean(collection["area"])
                        lpwc_graph.add((area_uri, RDF.type, lpwc_area_class))
                        lpwc_graph.add((area_uri, FOAF.name, Literal(area_name, datatype=XSD.string)))
                        lpwc_graph.add((collection_uri, has_area, area_uri))
                        area_mapping[collection["area"]] = area_id

                    else:
                        area_id = collection["area_id"]
                        area_uri = URIRef(lpwc_area + area_id)
                        lpwc_graph.add((collection_uri, has_area, area_uri))
                
            i += 1
            if i % 100 == 0:
                print('Processed {} Method entities'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        #write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()  
print("Done")