"""
    Input files: 
        evaluation-tables.json
        papers.json
        datasets.json
        methods.json
    Output file:
        evaluation-tables.nt

"""

from rdflib import URIRef, BNode, Literal
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, OWL, FOAF
from paperswithcode import PapersWithCodeClient 
import json
import re
import html2text
import markdown
from collections import deque


#Path to datasets.json, methods.json and papers.json input files
file_path_dataset = '.../datasets.json'
file_path_methods = '.../methods.json'
file_path_papers = '.../papers.json'
file_path_evaluation_tables = '.../evaluation-tables.json'


#Path to evaluation-tables.nt output file
ntriple_evaluation_tables_output_file_path = '.../evaluation-tables.nt'


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
lpwc_dataset_class = URIRef(lpwc_namespace_class + "/dataset")
lpwc_method_class = URIRef(lpwc_namespace_class + "/method")
lpwc_model_class = URIRef(lpwc_namespace_class + "/model")
lpwc_evaluation_class = URIRef(lpwc_namespace_class + "/evaluation")
lpwc_evaluation_result_class = URIRef(lpwc_namespace_class + "/evaluationresult")
lpwc_area_class = URIRef(lpwc_namespace_class + "/area")

#LinkedPapersWithCode classes used in this file
lpwc_paper = URIRef(lpwc_namespace + "/paper/")
lpwc_task = URIRef(lpwc_namespace + "/task/")
lpwc_dataset = URIRef(lpwc_namespace + "/dataset/")
lpwc_method = URIRef(lpwc_namespace + "/method/")
lpwc_model = URIRef(lpwc_namespace + "/model/")
lpwc_evaluation = URIRef(lpwc_namespace + "/evaluation/")
lpwc_evaluation_result = URIRef(lpwc_namespace + "/evaluationresult/")
lpwc_area = URIRef(lpwc_namespace + "/area/")

#LinkedPapersWithCode predicates used in this file
has_subtask = URIRef("https://linkedpaperswithcode.com/property/hasSubtask")
has_area  = URIRef("http://dbpedia.org/property/area")
has_task = URIRef("https://linkedpaperswithcode.com/property/hasTask")
has_evaluation = URIRef("https://linkedpaperswithcode.com/property/hasEvaluation")
has_dataset = URIRef("https://linkedpaperswithcode.com/property/hasDataset")
has_model = URIRef("https://linkedpaperswithcode.com/property/hasModel")
has_evaluation_result = URIRef("https://linkedpaperswithcode.com/property/hasEvaluationResult")

has_metric_name = URIRef("https://linkedpaperswithcode.com/property/metricName")
has_metric_value = URIRef("https://linkedpaperswithcode.com/property/metricValue")
uses_extra_training_data = URIRef("https://linkedpaperswithcode.com/property/usesExtraTrainingData")

used_dataset = URIRef("https://linkedpaperswithcode.com/property/usesDataset")


#Task Mapping
client = PapersWithCodeClient()

def get_all_tasks(client):
    page = 1  # Beginnen Sie mit Seite 1
    all_tasks = []

    while True:
        tasks = client.task_list(page=page)
        all_tasks.extend(tasks.results)

        if tasks.next_page is None:  # Wenn es keine nächste Seite gibt, beenden Sie die Schleife
            break

        page = tasks.next_page  # Ansonsten setzen Sie die nächste Seite auf die nächste zu durchsuchende Seite

    return all_tasks

task_list = get_all_tasks(client)
task_list.pop(0)

task_mapping = {}
for task in task_list:
    task_mapping[task.name] = task.id

print("Task Mapping Taks-Title : Task-ID created")


#Paper Mapping
paper_mapping = {}

with open(file_path_papers, 'r') as file:
    papers = json.load(file)

    for paper in papers:

        #paper-id
        paper_id = paper["paper_url"].replace("https://paperswithcode.com/paper/", "")
        paper_title = paper["title"]
        paper_mapping[paper_title] = paper_id

print("Paper Mapping Paper-Title : Paper-ID created")


#Dataset Mapping
dataset_mapping = {}

with open(file_path_dataset, 'r') as file:
    datasets = json.load(file)

    for dataset in datasets:

        #dataset-id
        dataset_id = dataset["url"].replace("https://paperswithcode.com/dataset/", "")
        dataset_name = dataset["name"]
        dataset_mapping[dataset_name] = dataset_id

print("Dataset Mapping Dataset-Name : Dataset-ID created")

#Area mapping
area_mapping = {}
with open(file_path_methods, 'r') as file:
    methods = json.load(file)

    for method in methods:

        if method["collections"] != None:
            for collection in method["collections"]:
                    area_id = collection["area_id"]
                    area_mapping[collection["area"]] = area_id

print("Area Mapping Area-Name : Area-ID created")


#recursive method for tasks (calls handle_dataset and handle_task)
def handle_task(task, g, parent=None):

    if task['task'] in task_mapping:
        task_id = clean_url(task_mapping[task['task']])
        task_uri = URIRef(lpwc_task + task_id)
        description = convert_markdown_to_plain_text(task['description'])
        description = clean(description)
        g.add((task_uri, DCTERMS.description, Literal(description, datatype=XSD.string)))

    else:
        task_id = clean_url(task['task'].replace(" ", "-").lower())
        task_uri = URIRef(lpwc_task + task_id)
        description = convert_markdown_to_plain_text(task['description'])
        description = clean(description)
        g.add((task_uri, DCTERMS.description, Literal(description, datatype=XSD.string)))


    if parent is not None:
        g.add((parent, has_subtask, task_uri))

    for category in task['categories']:
        if category in area_mapping:
            area_id = area_mapping[category]
            area_id = clean_url(area_id)
            area_uri = URIRef(lpwc_area + area_id)
            g.add((task_uri, has_area, area_uri))

        else:
            area_id = category.replace(" ", "-").lower()
            area_id = clean_url(area_id)
            area_uri = URIRef(lpwc_area + area_id)
            area_name = clean(category)
            g.add((area_uri, RDF.type, lpwc_area_class))
            g.add((area_uri, FOAF.name, Literal(area_name, datatype=XSD.string)))
            g.add((task_uri, has_area, area_uri))

    for dataset in task.get('datasets', []):
        handle_dataset(dataset, g, task_uri)

    for subtask in task.get('subtasks', []):
        handle_task(subtask, g, task_uri)


#method for dataset objects
def handle_dataset(dataset, g, task_uri):

    if dataset['dataset'] in dataset_mapping:
        dataset_id = dataset_mapping[dataset['dataset']]
        dataset_id = clean_url(dataset_id)
        dataset_uri = URIRef(lpwc_dataset + dataset_id)
    
    else:
        dataset_id = dataset['dataset'].replace(" ", "-").lower()
        dataset_id = clean_url(dataset_id)
        dataset_uri = URIRef(lpwc_dataset + dataset_id)


    if dataset["description"] != "":
        description = convert_markdown_to_plain_text(dataset["description"])
        description = clean(description)
        g.add((dataset_uri, DCTERMS.description, Literal(description, datatype=XSD.string)))


    row_counter = 0
    current_paper = ""
    current_model = ""
    task_id = task_uri.replace("https://linkedpaperswithcode.com/task/", "")
    dataset_id = dataset_uri.replace("https://linkedpaperswithcode.com/dataset/", "")
 
    if dataset.get('sota') is not None:
        for row in dataset['sota']['rows']:

            paper_title = row['paper_title']
            if paper_title in paper_mapping:
                paper_id = clean_url(paper_mapping[paper_title])
                paper_uri = URIRef(lpwc_paper + paper_id)

            else:
                paper_id = paper_title.replace(" ", "-").lower()
                paper_id = clean_url(paper_id)
                paper_uri = URIRef(lpwc_paper + paper_id)

            if current_paper != row['paper_title']:
                current_paper = row['paper_title']
                model_id = clean_url(row['model_name'].replace(" ", "-").lower())
                evaluation_uri = URIRef(lpwc_evaluation + paper_id + "/" + task_id + "/" + dataset_id + "/" + model_id)

                g.add((evaluation_uri, RDF.type, lpwc_evaluation_class))
                g.add((paper_uri, has_evaluation, evaluation_uri))

                model_id = clean_url(row['model_name'].replace(" ", "-").lower())
                model_uri = URIRef(lpwc_model + model_id)
                g.add((paper_uri, has_model, model_uri))

                g.add((paper_uri, used_dataset, dataset_uri))


            elif current_model != row['model_name']:
                current_model = row['model_name']
                model_id = clean_url(row['model_name'].replace(" ", "-").lower())
                evaluation_uri = URIRef(lpwc_evaluation + paper_id + "/" + task_id + "/" + dataset_id + "/" + model_id)

                g.add((evaluation_uri, RDF.type, lpwc_evaluation_class))
                g.add((paper_uri, has_evaluation, evaluation_uri))

                model_uri = URIRef(lpwc_model + model_id)
                g.add((paper_uri, has_model, model_uri))


            else:
                model_id = clean_url(row['model_name'].replace(" ", "-").lower())
                evaluation_uri = URIRef(lpwc_evaluation + paper_id + "/" + task_id + "/" + dataset_id + "/" + model_id)

            #has_task
            g.add((evaluation_uri, has_task, task_uri))

            #has_dataset
            g.add((evaluation_uri, has_dataset, dataset_uri))

            #has_model
            model_id = clean_url(row['model_name'].replace(" ", "-").lower())
            model_uri = URIRef(lpwc_model + model_id)
            model_name = clean(row['model_name'])
            g.add((model_uri, RDF.type, lpwc_model_class))
            g.add((model_uri, FOAF.name, Literal(model_name, datatype=XSD.string)))
            g.add((evaluation_uri, has_model, model_uri))

            #has_metric (name and value)
            if row['metrics'] is not None:
                for metric_name, metric_value in row['metrics'].items():
                    
                    #initialize evaluationresult entities
                    evaluation_id = evaluation_uri.replace("https://linkedpaperswithcode.com/evaluation/", "")
                    metric_name_id = metric_name.replace(" ", "-").lower()
                    metric_name_id = clean_url(metric_name_id)
                    evaluation_result_uri = URIRef(lpwc_evaluation_result + evaluation_id + "/" + metric_name_id)
                    g.add((evaluation_result_uri, RDF.type, lpwc_evaluation_result_class))
                    g.add((evaluation_uri, has_evaluation_result, evaluation_result_uri))

                    g.add((evaluation_result_uri, has_metric_name, Literal(metric_name, datatype=XSD.string)))
                    g.add((evaluation_result_uri, has_metric_value, Literal(metric_value, datatype=XSD.string)))

                    #uses_additional_data
                    if row['uses_additional_data'] == True:
                        g.add((evaluation_result_uri, uses_extra_training_data, Literal(True, datatype=XSD.boolean)))
                    elif row['uses_additional_data'] == False:
                        g.add((evaluation_result_uri, uses_extra_training_data, Literal(False, datatype=XSD.boolean)))

        
#breadth-first search of the objects
def breadth_first_search(obj, g):
    queue = deque([(None, obj, 0)])
    while queue:
        key, current_data, depth = queue.popleft()
        if isinstance(current_data, dict) and 'task' in current_data:
            handle_task(current_data, g)
        elif isinstance(current_data, list):
            for item in current_data:
                queue.append((key, item, depth+1))
        elif isinstance(current_data, dict):
            for k, v in current_data.items():
                queue.append((k, v, depth+1))

#method to create the final graph and output it to a file
def create_graph(data):
    g = Graph()
    breadth_first_search(data, g)
    serialized_graph = g.serialize(format='nt')

    #specify the path to the output file
    path = ntriple_evaluation_tables_output_file_path
    # Write to file
    with open(path, 'wb') as f:
        f.write(serialized_graph.encode('utf-8'))



with open(file_path_evaluation_tables, 'r') as f:
    data = json.load(f)

create_graph(data)
print("Done")