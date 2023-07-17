## Entity Embeddings for Linked Papers With Code

### Pre-processing and Embedding training

*01:* Extracts triples from full RDF dump of Linked Papers with Code and map all URIs to integers. 

*02:* Train entity embeddings 


### Evaluation results

The best values for the metrics mean rank (MR) and Hits@N are marked bold.

| Metric  | TransE | DistMult | ComplEx | RotatE |
|---------|-------:|---------:|--------:|----------:|
| MR      | **2239.26** |  9448.88  |  25,624.13 |   8830.03  |
| Hits@1  |  **0.2395** |  0.1931   |  0.1655  |   0.1146   |
| Hits@3  |  **0.3852** |  0.3204   |  0.2814  |   0.1921   |
| Hits@10 |  **0.5425** |  0.4856   |  0.4390  |   0.3133   |


### Technical details