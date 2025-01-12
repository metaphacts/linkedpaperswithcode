The jupyter notebook [link-lpwc-to-mlsea.ipynb](./link-lpwc-to-mlsea.ipynb) links entities of the RDF knowledge graphs Linked Papers With Code (LPWC) (https://linkedpaperswithcode.com) and MLSea-KG (https://w3id.org/mlsea and https://w3id.org/mlsea-kg).
It links publication, repository and datset entities.

It uses the corresponding RDF files in .nt format as input.

Input:
- Linked Papers With Code Dump in .nt format (accessible at https://zenodo.org/records/13881433)
- The file pwc_1.nt.gz from the MLSea Dump (accessible at https://zenodo.org/records/11264641)

Output:
- .../paper-sameas-links.nt --> The sameas links between the publication entities of LPWC and MLSea
- .../repository-sameas-links.nt --> The sameas links between the repository entities of LPWC and MLSea
- .../dataset-sameas-links.nt --> The sameas links between the dataset entities of LPWC and MLSea