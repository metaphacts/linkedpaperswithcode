"""
    Input files: 
        papers.json
        and API (https://dblp.org/search/venue/api?)
    Output file:
        conferences.nt
"""

from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import json
import re
import html2text
import markdown
import requests
from bs4 import BeautifulSoup

#Path to papers.json input file
file_path = '.../papers.json'

#Path to conferences.nt output file
ntriple_output_file_path = ".../conferences.nt"


def preprocess_pwc_proceeding_string(proceeding):
    pattern = re.compile(r'(\w+)( \d{4})?( \d+)?')
    match = pattern.match(proceeding)
    try:
        return "".join(match.group(1, 2)).strip()
    except TypeError:
        return match.group(1)
    except AttributeError:
        return proceeding


def get_conference_info(query):
    url = f"https://dblp.org/search/venue/api?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        venue = soup.find('venue').text 
    except AttributeError:
        venue = ""
    try:
        acronym = soup.find('acronym').text
    except AttributeError:
        acronym = ""
    try:
        conf_url = soup.find('url').text
    except AttributeError:
        conf_url = ""
    return venue, acronym, conf_url

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
lpwc_conference_class = URIRef(lpwc_namespace_class + "/conference")
lpwc_method_class = URIRef(lpwc_namespace_class + "/method")
lpwc_category_class = URIRef(lpwc_namespace_class + "/category") #collectio

#LinkedPapersWithCode classes used in this file
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
lpwc_task = URIRef(lpwc_namespace + "/task/")
lpwc_conference = URIRef(lpwc_namespace + "/conference/")
lpwc_method = URIRef(lpwc_namespace + "/method/")
lpwc_category = URIRef(lpwc_namespace + "/methods/category/") #collection


#LinkedPapersWithCode predicates used in this file
has_arxiv_id = URIRef("http://purl.org/spar/fabio/hasArXivId")
has_url = URIRef("http://purl.org/spar/fabio/hasURL")
has_url_abs = URIRef("https://linkedpaperswithcode.com/property/hasURLAbstract")
has_dblp_url = URIRef("https://linkedpaperswithcode.com/property/dblpURL")
has_acronym = URIRef("https://dbpedia.org/property/acronym")
has_conference = URIRef("https://linkedpaperswithcode.com/property/hasConference")
has_task = URIRef("https://linkedpaperswithcode.com/property/hasTask")
has_method = URIRef("https://linkedpaperswithcode.com/property/hasMethod")
has_main_collection = URIRef("https://linkedpaperswithcode.com/property/mainCollection")
has_parent = URIRef("https://linkedpaperswithcode.com/property/hasParent")


lpwc_proceedings_graph = Graph()
proceeding_list = []

i = 0
with open(ntriple_output_file_path, "w", encoding="utf-8") as g:
    with open(file_path, 'r') as file:
        papers = json.load(file)
        for paper in papers:
     
            #proceeding
            if paper["proceeding"] is not None:
                proceeding_name = paper["proceeding"]
                proceeding_name = preprocess_pwc_proceeding_string(proceeding_name)
                proceeding_name = clean_url(proceeding_name)
                if proceeding_name not in proceeding_list:
                    proceeding_list.append(proceeding_name)
                    proceeding_uri = URIRef(lpwc_conference + proceeding_name.replace(" ", "-").lower())
                    proceeding, acronym, conf_url = get_conference_info(proceeding_name)
                    lpwc_proceedings_graph.add((proceeding_uri, RDF.type, lpwc_conference_class))
                    if proceeding != "":
                        lpwc_proceedings_graph.add((proceeding_uri, FOAF.name, Literal(proceeding, datatype=XSD.string)))
                    if acronym != "":
                        lpwc_proceedings_graph.add((proceeding_uri, has_acronym, Literal(acronym, datatype=XSD.string)))
                    if acronym == "":
                        lpwc_proceedings_graph.add((proceeding_uri, has_acronym, Literal(proceeding_name, datatype=XSD.string)))
                    if conf_url != "":
                        lpwc_proceedings_graph.add((proceeding_uri, has_dblp_url, Literal(conf_url, datatype=XSD.anyURI)))
            
            i += 1
            if i % 1000 == 0:
                print('Processed {} proceeding entities'.format(i))

            if i % 100 == 0:
                g.write(lpwc_proceedings_graph.serialize(format='nt'))
                lpwc_proceedings_graph = Graph()


        #write the last part
        if not i % 100 == 0:
            g.write(lpwc_proceedings_graph.serialize(format='nt'))
            lpwc_proceedings_graph = Graph()
        
g.close()
print("Done")