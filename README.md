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
The scripts for the Data transformation based on the [Paperswithcode dataset snapshot](https://github.com/paperswithcode/paperswithcode-data) to construct the Knowledge graph are in the folder [transformation-scripts](./transformation-scripts).

### Entity Linking 
The scripts for Linking the Entities of Linked Papers With Code to SemOpenAlex and Wikidata are in the folder [entity-linking-scripts](./entity-linking-scripts).

## Knowledge Graph Embeddings
The scripts for generating the Knowledge Graph Embeddings and the Evaluation Results of the diffrent Knowledge Graph Embeddings Models are in the folder [embeddings-generation](./embeddings-generation).

