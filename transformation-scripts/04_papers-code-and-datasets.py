"""
    Input files: 
        papers_code.json
        datasets.json
    Output files:
        papers_code.nt
        datasets.nt
"""

from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
import json
import re
import html2text
import markdown


#Path to methopapers_code.json and datasets.json input files
file_path_paper_code = '.../papers_code.json'
file_path_datasets = '.../datasets.json'

#Path to papers_code.nt and datasets.nt output files
ntriple_paper_code_output_file_path = ".../papers_code.nt"
ntriple_datasets_output_file_path = ".../datasets.nt"


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
    }, {
        "search": re.compile(r'\^'),
        "replace": '',
        "comment": "caret"
    }, {
        "search": re.compile(r'\$'),
        "replace": '',
        "comment": "Dollar sign"
    }, {
        "search": re.compile(r'\{'),
        "replace": '',
        "comment": "Opening curly brace"
    }, {
        "search": re.compile(r'\}'),
        "replace": '',
        "comment": "Closing curly brace"
    }, {
        "search": re.compile(r'\('),
        "replace": '',
        "comment": "Opening parenthesis"
    }, {
        "search": re.compile(r'\)'),
        "replace": '',
        "comment": "Closing parenthesis"
    }, {
        "search": re.compile(r':'),
        "replace": '',
        "comment": "Colon"
    }, {
        "search": re.compile(r','),
        "replace": '',
        "comment": "Comma"
    }, {
        "search": re.compile(r'>'),
        "replace": '',
        "comment": "Greater than"
    }, {
        "search": re.compile(r'<'),
        "replace": '',
        "comment": "Less than"
    }, {
        "search": re.compile(r'---'),
        "replace": '',
        "comment": "Triple dash"
    }, {
        "search": re.compile(r'--'),
        "replace": '',
        "comment": "Double dash"
    }, {
        "search": re.compile(r'\+'),
        "replace": '',
        "comment": "Plus sign"
    }, {
        "search": re.compile(r'\['),
        "replace": '',
        "comment": "Opening square bracket"
    }, {
        "search": re.compile(r'\]'),
        "replace": '',
        "comment": "Closing square bracket"
    }, {
        "search": re.compile(r'\|'),
        "replace": '',
        "comment": "Pipe"
    }, {
        "search": re.compile(r'%'),
        "replace": '',
        "comment": "Percent sign"
    }, {
        "search": re.compile(r'\xa0'),
        "replace": '',
        "comment": "Non-breaking space"
    }, {
        "search": re.compile(r'!'),
        "replace": '',
        "comment": "Exclamation mark"
    }, {
        "search": re.compile(r'\s'),
        "replace": '',
        "comment": "Whitespace"
    }, {
        "search": re.compile(r'%22'),
        "replace": '',
        "comment": "Quotation mark"
    }, {
        "search": re.compile(r'#'),
        "replace": '',
        "comment": "Hash"
    }, {
        "search": re.compile(r'@'),
        "replace": '',
        "comment": "At sign"
    }, {
        "search": re.compile(r'\*'),
        "replace": '',
        "comment": "Asterisk"
    }
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
lpwc_repository_class = URIRef(lpwc_namespace_class + "/repository")
lpwc_dataset_class = URIRef(lpwc_namespace_class + "/dataset")
lpwc_dataloader_class = URIRef(lpwc_namespace_class + "/dataloader")
lpwc_repositoryreferences_class = URIRef(lpwc_namespace_class + "/repositoryreferences")

#LinkedPapersWithCode classes used in this file
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
lpwc_task = URIRef(lpwc_namespace + "/task/")
lpwc_repository = URIRef(lpwc_namespace + "/repository/")
lpwc_dataset = URIRef(lpwc_namespace + "/dataset/")
lpwc_data_loader = URIRef(lpwc_namespace + "/dataloader/")
lpwc_repository_references = URIRef(lpwc_namespace + "/repositoryreferences/")


#LinkedPapersWithCode predicates used in this file
has_repository = URIRef("https://linkedpaperswithcode.com/property/hasRepository")
has_official_repository = URIRef("https://linkedpaperswithcode.com/property/hasOfficialRepository")
has_url = URIRef("http://purl.org/spar/fabio/hasURL")
paper_mentions_repository = URIRef("https://linkedpaperswithcode.com/property/paperMentionsRepository")
repository_mentions_paper = URIRef("https://linkedpaperswithcode.com/property/repositoryMentionsPaper")
has_framework = URIRef("https://linkedpaperswithcode.com/property/hasFramework")

has_full_name = URIRef("https://dbpedia.org/property/fullname")
introduced_by = URIRef("https://linkedpaperswithcode.com/property/introducedBy")
has_modality = URIRef("https://linkedpaperswithcode.com/property/modality")
used_for_task = URIRef("https://linkedpaperswithcode.com/property/usedForTask")
has_variant = URIRef("https://linkedpaperswithcode.com/property/hasVariant") 
num_papers = URIRef("https://linkedpaperswithcode.com/property/numberPapers") 
has_data_loader = URIRef("https://linkedpaperswithcode.com/property/hasDataLoader")
has_repo_reference = URIRef("https://linkedpaperswithcode.com/property/hasRepositoryReferences")


#papers_code.json

lpwc_graph = Graph()
repo_uri_list = []

i = 0
with open(ntriple_paper_code_output_file_path, "w", encoding="utf-8") as g:
    # JSON-Datei öffnen und als Liste von Objekten laden
    with open(file_path_paper_code, 'r') as file:
        paper_code = json.load(file)

        for paper_code_entry in paper_code:

            #paper_url paper_uri
            paper_id = paper_code_entry["paper_url"].replace("https://paperswithcode.com/paper/", "")
            paper_uri = URIRef(lpwc_paper + paper_id)
           
            #repo_url repo_uri
            repo_url = clean_url(paper_code_entry["repo_url"])
            repo_id = repo_url.replace("https://", "").replace("http://", "")
            repo_id = repo_id.lower()
            repo_uri = URIRef(lpwc_repository + repo_id)

            #Auxiliary class for n-array relations (repositoryreferences)
            repo_references_uri = URIRef(lpwc_repository_references + paper_id + "/" + repo_id)
            lpwc_graph.add((repo_references_uri, RDF.type, lpwc_repositoryreferences_class))
            lpwc_graph.add((paper_uri, has_repo_reference, repo_references_uri))
            lpwc_graph.add((repo_references_uri, has_repository, repo_uri))
            
            
            if not repo_uri in repo_uri_list:
                repo_uri_list.append(repo_uri)
                lpwc_graph.add((repo_uri, RDF.type, lpwc_repository_class))
                lpwc_graph.add((repo_uri, has_url, Literal(repo_url, datatype=XSD.anyURI)))

                #framework
                if paper_code_entry["framework"] != "none":
                    framework_name = clean(paper_code_entry["framework"])
                    lpwc_graph.add((repo_uri, has_framework, Literal(framework_name, datatype=XSD.string)))

            #is_official
            if paper_code_entry["is_official"] == True:
                lpwc_graph.add((paper_uri, has_official_repository, repo_uri))

            if paper_code_entry["is_official"] == False:
                lpwc_graph.add((paper_uri, has_repository, repo_uri))

            #mentioned_in_paper (in repositoryreferences)
            if paper_code_entry["mentioned_in_paper"] == True:
                lpwc_graph.add((repo_references_uri, paper_mentions_repository, Literal(True, datatype=XSD.boolean)))

            if paper_code_entry["mentioned_in_paper"] == False:
                lpwc_graph.add((repo_references_uri, paper_mentions_repository, Literal(False, datatype=XSD.boolean)))
            
            #mentioned_in_github (in repositoryreferences)
            if paper_code_entry["mentioned_in_github"] == True:
                lpwc_graph.add((repo_references_uri, repository_mentions_paper, Literal(True, datatype=XSD.boolean)))
            
            if paper_code_entry["mentioned_in_github"] == False:
                lpwc_graph.add((repo_references_uri, repository_mentions_paper, Literal(False, datatype=XSD.boolean)))
            

            i += 1
            if i % 2000 == 0:
                print('Processed {} paper_code entities'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        # Write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()


#datasets.json
lpwc_graph = Graph()


i = 0
with open(ntriple_datasets_output_file_path, "w", encoding="utf-8") as g:
    # JSON-Datei öffnen und als Liste von Objekten laden
    with open(file_path_datasets, 'r') as file:
        datasets = json.load(file)
        for dataset in datasets:

            #dataset-id
            dataset_id = dataset["url"].replace("https://paperswithcode.com/dataset/", "")
            dataset_uri = URIRef(lpwc_dataset + dataset_id)
            lpwc_graph.add((dataset_uri, RDF.type, lpwc_dataset_class))

            #name
            if dataset["name"] != "" and dataset["name"] is not None:
                dataset_name = dataset["name"]
                dataset_name = clean(dataset_name)
                lpwc_graph.add((dataset_uri, DCTERMS.title, Literal(dataset_name, datatype=XSD.string)))

            #full_name
            if dataset["full_name"] != "" and dataset["full_name"] is not None:
                dataset_full_name = dataset["full_name"]
                dataset_full_name = clean(dataset_full_name)
                lpwc_graph.add((dataset_uri, has_full_name, Literal(dataset_full_name, datatype=XSD.string)))

            #homepage
            if dataset["homepage"] != "" and dataset["homepage"] is not None:
                dataset_homepage = dataset["homepage"]
                dataset_homepage = clean_url(dataset_homepage)
                lpwc_graph.add((dataset_uri, FOAF.homepage, Literal(dataset_homepage, datatype=XSD.anyURI)))

            #description
            if dataset["description"] != "" and dataset["description"] is not None:
                dataset_description = dataset["description"]
                dataset_description = convert_markdown_to_plain_text(dataset_description)
                dataset_description = clean(dataset_description)
                lpwc_graph.add((dataset_uri, DCTERMS.description, Literal(dataset_description, datatype=XSD.string)))

            #paper
            if dataset["paper"] != None:

                if dataset["paper"]["url"].startswith("https://paperswithcode.com/paper/"):
                    paper_id = dataset["paper"]["url"].replace("https://paperswithcode.com/paper/", "")
                    paper_uri = URIRef(lpwc_paper + paper_id)
                    lpwc_graph.add((dataset_uri, introduced_by, paper_uri))

                else:
                    paper_id = dataset["paper"]["url"].replace(" ", "-").lower()
                    paper_id = paper_id.replace("https://", "").replace("http://", "")
                    paper_uri = URIRef(lpwc_paper + paper_id)

                    lpwc_graph.add((paper_uri, RDF.type, lpwc_paper_class))
                    lpwc_graph.add((dataset_uri, introduced_by, paper_uri))
                    
                    #title
                    paper_title = clean(dataset["paper"]["title"])
                    lpwc_graph.add((paper_uri, DCTERMS.title , Literal(paper_title, datatype=XSD.string)))

                    #url
                    paper_url = clean_url(dataset["paper"]["url"])
                    lpwc_graph.add((paper_uri, has_url, Literal(paper_url, datatype=XSD.anyURI)))


            #introduced_date
            if dataset["introduced_date"] != "" and dataset["introduced_date"] is not None:
                dataset_introduced_date = dataset["introduced_date"]
                lpwc_graph.add((dataset_uri, DCTERMS.issued, Literal(dataset_introduced_date, datatype=XSD.date)))

            #warnings (not relevant)

            #modalities
            if dataset["modalities"] != []:
                for modality in dataset["modalities"]:
                    modality = clean(modality)
                    lpwc_graph.add((dataset_uri, has_modality, Literal(modality, datatype=XSD.string)))

            #tasks
            if dataset["tasks"] != []:
                for task in dataset["tasks"]:
                    task_id = task["url"].replace("https://paperswithcode.com/task/", "")
                    task_uri = URIRef(lpwc_task + task_id)
                    lpwc_graph.add((dataset_uri, used_for_task, task_uri))

            #languages
            if dataset["languages"] != []:
                for language in dataset["languages"]:
                    language = clean(language)
                    lpwc_graph.add((dataset_uri, DCTERMS.language, Literal(language, datatype=XSD.string)))

            #variants
            if dataset["variants"] != []:
                for variant in dataset["variants"]:
                    variant = clean(variant)
                    lpwc_graph.add((dataset_uri, has_variant, Literal(variant, datatype=XSD.string)))

            #num_papers
            if dataset["num_papers"] is not None:
                dataset_num_papers = dataset["num_papers"]
                lpwc_graph.add((dataset_uri, num_papers, Literal(dataset_num_papers, datatype=XSD.integer)))

            #data_loaders
            if dataset["data_loaders"] != []:
                for data_loader in dataset["data_loaders"]:
                    if data_loader["url"] != "" and data_loader["url"] is not None:
                        data_loader_url = clean_url(data_loader["url"])
                        data_loader_id = data_loader_url.replace("https://", "").replace("http://", "")
                        data_loader_uri = URIRef(lpwc_data_loader + data_loader_id)
                        lpwc_graph.add((data_loader_uri, RDF.type, lpwc_dataloader_class))
                        lpwc_graph.add((data_loader_uri, FOAF.homepage, Literal(data_loader_url, datatype=XSD.anyURI)))
                        lpwc_graph.add((dataset_uri, has_data_loader, data_loader_uri))

                        if data_loader["repo"] != "" and data_loader["repo"] is not None:
                            data_loader_repo_url = clean_url(data_loader["repo"])
                            data_loader_repo_id = data_loader_repo_url.replace("https://", "").replace("http://", "")
                            data_loader_repo_uri = URIRef(lpwc_repository + data_loader_repo_id)

                            #Überprüfen ob es Reposirory schon gibt 
                            if not data_loader_repo_uri in repo_uri_list:
                                lpwc_graph.add((data_loader_repo_uri, RDF.type, lpwc_repository_class))
                                lpwc_graph.add((data_loader_repo_uri, has_url, Literal(data_loader_repo_url, datatype=XSD.anyURI)))

                                lpwc_graph.add((data_loader_uri, has_repository, data_loader_repo_uri))

                                if data_loader["frameworks"] != []:
                                    for framework in data_loader["frameworks"]:
                                        framework = clean(framework)
                                        lpwc_graph.add((data_loader_repo_uri, has_framework, Literal(framework, datatype=XSD.string)))   

                            else:
                                lpwc_graph.add((data_loader_uri, has_repository, data_loader_repo_uri))


            i += 1
            if i % 1000 == 0:
                print('Processed {} dataset entities'.format(i))

            if i % 100 == 0:
                g.write(lpwc_graph.serialize(format='nt'))
                lpwc_graph = Graph()


        #write the last part
        if not i % 100 == 0:
            g.write(lpwc_graph.serialize(format='nt'))
            lpwc_graph = Graph()
        
g.close()
print("Done")
