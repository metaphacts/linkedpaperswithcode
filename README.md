# LinkedPaperswithcode

LinkedPaperswithcode is a RDF knoweldge graph containing detailed information about machine learning papers, repositories, datasets, methods, tasks, models, evaluations and related information.

LinkedPaperswithcode is based on [Paperswithcode](https://paperswithcode.com). The underlying [dataset snapshot](https://github.com/paperswithcode/paperswithcode-data) of Paperswithcode are regenerated daily. With the scripts provided in this repository, the LinkedPaperswithcode knowledeg graph can be re-generated based on the snapshot.



<figure>
    <img width="753" height="542" src="linkedpaperswithcode-schema.png"
         alt="Schema of Linked Papers With Code">
    <figcaption>Schema of Linked Papers With Code</figcaption>
</figure>


## Knowledge Graph Construction 

### Data transformation
To construct the Linked Papers With Code Knowledge Graph based o the [Paperswithcode dataset snapshot](https://github.com/paperswithcode/paperswithcode-data) we use the following [python scripts](./transformation-scripts):

1. [01_papers.py](./transformation-scripts/01_papers.py)
2. [02_conferences.py](./transformation-scripts/02_conferences.py)
3. [03_methods.py](./transformation-scripts/03_methods.py)
4. [04_papers-code-and-datasets.py](./transformation-scripts/04_papers-code-and-datasets.py)
5. [05_evaluation-tables.py](./transformation-scripts/05_evaluation-tables.py)
6. [06_validation-and-formats.py](./transformation-scripts/06_validation-and-formats.py)

### Entity Linking 
The scripts for Linking the Entities of Linked Papers With Code to SemOpenAlex and Wikidata are in the folder [entity-linking-scripts](./entity-linking-scripts).

## Knowledge Graph Embeddings
The scripts for generating the Knowledge Graph Embeddings and the Evaluation Results of the different Knowledge Graph Embeddings Models are in the folder [embeddings-generation](./embeddings-generation).

