""" 
    Input files: 
        papers.json 
        methods.json
        and API (https://paperswithcode.com/api/v1/)
    Output files:
        papers.nt
        tasks.nt
"""

from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import json
import re
import html2text
import markdown
from paperswithcode import PapersWithCodeClient 

#Path to methods.json and papers.json input files
file_path_methods = '.../methods.json'
file_path_papers = '.../papers.json'

#Path to tasks.nt and papers.nt output files
ntriple_tasks_output_file_path = ".../tasks.nt"
ntriple_papers_output_file_path = ".../papers.nt"


def preprocess_pwc_proceeding_string(proceeding):
    pattern = re.compile(r'(\w+)( \d{4})?( \d+)?')
    match = pattern.match(proceeding)
    try:
        return "".join(match.group(1, 2)).strip()
    except TypeError:
        return match.group(1)
    except AttributeError:
        return proceeding

def convert_markdown_to_plain_text(md_string):
    html = markdown.markdown(md_string)
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.ignore_emphasis = True
    plain_text = text_maker.handle(html)
    return plain_text


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


#Info for namespaces used in LinkedPapersWithCode
lpwc_namespace = "https://linkedpaperswithcode.com"
lpwc_namespace_class = "https://linkedpaperswithcode.com/class"

lpwc_paper_class = URIRef(lpwc_namespace_class + "/paper")
lpwc_task_class = URIRef(lpwc_namespace_class + "/task")
lpwc_conference_class = URIRef(lpwc_namespace_class + "/conference")
lpwc_method_class = URIRef(lpwc_namespace_class + "/method")
lpwc_category_class = URIRef(lpwc_namespace_class + "/category")

#LinkedPapersWithCode classes used in this file
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
lpwc_task = URIRef(lpwc_namespace + "/task/")
lpwc_conference = URIRef(lpwc_namespace + "/conference/")
lpwc_method = URIRef(lpwc_namespace + "/method/")
lpwc_category = URIRef(lpwc_namespace + "/methods/category/")


#LinkedPapersWithCode predicates used in this file
has_arxiv_id = URIRef("http://purl.org/spar/fabio/hasArXivId")
has_url = URIRef("http://purl.org/spar/fabio/hasURL")
has_url_abs = URIRef("https://linkedpaperswithcode.com/property/hasURLAbstract")
has_dblp_url = URIRef("https://linkedpaperswithcode.com/property/dblpURL")
has_acronym = URIRef("http://dbpedia.org/property/acronym")
has_conference = URIRef("https://linkedpaperswithcode.com/property/hasConference")
has_task = URIRef("https://linkedpaperswithcode.com/property/hasTask")
has_method = URIRef("https://linkedpaperswithcode.com/property/hasMethod")
has_main_category = URIRef("https://linkedpaperswithcode.com/property/mainCategory")
has_parent = URIRef("https://linkedpaperswithcode.com/property/hasParent")


#tasks via api
client = PapersWithCodeClient()

def get_all_tasks(client):
    page = 1  # Beginnen Sie mit Seite 1
    all_tasks = []

    while True:
        tasks = client.task_list(page=page)
        all_tasks.extend(tasks.results)

        if tasks.next_page is None:  # Wenn es keine nächste Seite gibt, beende die Schleife
            break

        page = tasks.next_page  # Ansonsten setzen die nächste Seite auf die nächste zu durchsuchende Seite

    return all_tasks

task_list = get_all_tasks(client)
task_list.pop(0) #remove the "task" task with no id and description


#create a mapping from task-name to task-id
lpwc_graph = Graph()
task_mapping = {}
i = 0
with open(ntriple_tasks_output_file_path, "w", encoding="utf-8") as g:
    for task in task_list:

        task_mapping[task.name] = task.id
        
        #task-id
        task_uri = URIRef(lpwc_task + task.id)
        lpwc_graph.add((task_uri, RDF.type, lpwc_task_class))

        #task-name
        task_name = clean(task.name)
        lpwc_graph.add((task_uri, FOAF.name, Literal(task_name, datatype=XSD.string)))

        #task-description
        if task.description != "":
            task_description = convert_markdown_to_plain_text(task.description)
            task_description = clean(task_description)
            lpwc_graph.add((task_uri, DCTERMS.description, Literal(task_description, datatype=XSD.string)))

        i += 1
        if i % 1000 == 0:
            print('Processed {} task entities'.format(i))

        if i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()


    #write the last part
    if not i % 100 == 0:
        g.write(lpwc_graph.serialize(format='nt'))
        lpwc_graph = Graph()
    
g.close()


#methods.json
#creates a mapping from method-name to method-id
method_mapping = {}

with open(file_path_methods, 'r') as file:
    methods = json.load(file)
    for method in methods:
        method_id = method["url"].replace("https://paperswithcode.com/method/", "")
        method_name = method["name"]
        method_mapping[method_name] = method_id



#papers.json
#transform papers.json file
lpwc_graph = Graph()

i = 0
with open(ntriple_papers_output_file_path, "w", encoding="utf-8") as g:
    with open(file_path_papers, 'r') as file:
        papers = json.load(file)
        for paper in papers:

            #paper-id
            paper_id = paper["paper_url"].replace("https://paperswithcode.com/paper/", "")
            paper_uri = URIRef(lpwc_paper + paper_id)
            lpwc_graph.add((paper_uri, RDF.type, lpwc_paper_class))

            #arxiv_id
            if paper["arxiv_id"] != "" and paper["arxiv_id"] is not None:
                arxiv_id = clean(paper["arxiv_id"])
                lpwc_graph.add((paper_uri, has_arxiv_id, Literal(arxiv_id, datatype=XSD.string)))

            #title
            if paper["title"] is not None:
                paper_title = clean(paper["title"])
                lpwc_graph.add((paper_uri, DCTERMS.title , Literal(paper_title, datatype=XSD.string)))

            #abstract
            if paper["abstract"] != "" and paper["abstract"] is not None:
                paper_abstract = convert_markdown_to_plain_text(paper["abstract"])
                paper_abstract = clean(paper_abstract)
                lpwc_graph.add((paper_uri, DCTERMS.abstract, Literal(paper_abstract, datatype=XSD.string)))

            #url_abs
            if paper["url_abs"] != "" and paper["url_abs"] is not None:
                paper_url_abs = clean_url(paper["url_abs"])
                lpwc_graph.add((paper_uri, has_url_abs, Literal(paper_url_abs, datatype=XSD.anyURI)))
                
            #url_pdf
            if paper["url_pdf"] != "" and paper["url_pdf"] is not None:
                paper_url_pdf = clean_url(paper["url_pdf"])
                lpwc_graph.add((paper_uri, has_url, Literal(paper_url_pdf, datatype=XSD.anyURI)))

            #date
            if paper["date"] != "":
                paper_date = paper["date"]
                lpwc_graph.add((paper_uri, DCTERMS.date, Literal(paper_date, datatype=XSD.date)))

            #proceeding
            if paper["proceeding"] is not None:
                proceeding_name = paper["proceeding"]
                proceeding_name = preprocess_pwc_proceeding_string(proceeding_name)
                proceeding_name = clean_url(proceeding_name)
                proceeding_uri = URIRef(lpwc_conference + proceeding_name.replace(" ", "-").lower())
                lpwc_graph.add((paper_uri, has_conference, proceeding_uri))

            #tasks
            if paper["tasks"] != []:
                for task in paper["tasks"]:
                    if task in task_mapping:
                        task_id = clean_url(task_mapping[task])
                        task_uri = URIRef(lpwc_task + task_id)
                        lpwc_graph.add((paper_uri, has_task, task_uri))
                    else:     
                        task_uri = URIRef(lpwc_task + clean_url(task.replace(" ", "-").lower()))
                        lpwc_graph.add((task_uri, RDF.type, lpwc_task_class))
                        lpwc_graph.add((paper_uri, has_task, task_uri))
                        

            #methods
            if paper["methods"] != []:
                for method in paper["methods"]:
                        method_name = method["name"]
                        if method_name in method_mapping:
                            method_id = clean_url(method_mapping[method_name])
                            method_uri = URIRef(lpwc_method + method_id)
                            lpwc_graph.add((paper_uri, has_method, method_uri))
                        
                        else:
                            method_id = clean_url(method["name"].replace(" ", "-").lower())
                            method_uri = URIRef(lpwc_method + method_id)
                            lpwc_graph.add((paper_uri, has_method, method_uri))


                        if method["main_collection"] is not None:
                            main_collection_name = clean_url(method["main_collection"]["name"].replace(" ", "-").lower())
                            main_collection_uri = URIRef(lpwc_category + main_collection_name)
                            lpwc_graph.add((method_uri, has_main_category, main_collection_uri))

                            if method["main_collection"]["parent"] is not None:
                                main_collection_parent_name = clean_url(method["main_collection"]["parent"].replace(" ", "-").lower())
                                main_collection_parent_uri = URIRef(lpwc_category + main_collection_parent_name)
                                lpwc_graph.add((main_collection_uri, has_parent, main_collection_parent_uri))


            i += 1
            if i % 1000 == 0:
                print('Processed {} Paper entities'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        #write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()  
print("Done")