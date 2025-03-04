# DATA.md

## **Data Overview**
This file defines the conceptual structure of the database systems explaining node types, relationships and how the data will be model. 

## Data Files
The dataset includes:
- **nodes.tsv** (About the entities like genes, diseases, compounds)
- **edges.tsv** (Relationships between entities)
- **sample_nodes.tsv** (Snippet of `nodes.tsv`)
- **sample_edges.tsv** (Snippet of `edges.tsv`)

### **Nodes Overview**
Each node represents a biological entity and is categorized by `kind`. Below is a summary of node structure derived from `sample_nodes.tsv`:

| **Property** | **Description** | **Example** |
|-------------|----------------|-------------|
| `id`        | Unique identifier for the node | `Anatomy::UBERON:0000002` |
| `name`      | Human-readable name of the node | `uterine cervix` |
| `kind`      | Type of entity (e.g., Anatomy, Disease, Gene, Compound) | `Anatomy` |

### **Relationships Overview**
Relationships define interactions between nodes based on `metaedge` from `sample_edges.tsv`. Below is a summary of relationship structure:

| **Property**  | **Description**  | **Example**  |
|--------------|----------------|-------------|
| `source`    | Origin node identifier | `Disease::DOID:0050156` |
| `metaedge`  | Type of relationship between nodes | `DdG` |
| `target`    | Destination node identifier | `Gene::1` |

### **Understanding Relationship Types**
The `metaedge` field in the edges dataset represents different types of relationships between biological entities. Below is an explanation of selected metaedges from HetioNet, including their corresponding Neo4j relationship expressions using Cypher syntax.

| **Metaedge** | **Abbreviation** | **Meaning** | **Neo4j Relationship** |
|-------------|----------------|------------|------------------------|
| Anatomy–downregulates–Gene | `AdG` | Anatomy downregulates Gene | `(:Anatomy)-[:DOWNREGULATES]->(:Gene)` |
| Anatomy–expresses–Gene | `AeG` | Anatomy expresses Gene | `(:Anatomy)-[:EXPRESSES]->(:Gene)` |
| Anatomy–upregulates–Gene | `AuG` | Anatomy upregulates Gene | `(:Anatomy)-[:UPREGULATES]->(:Gene)`| 
| Compound–binds–Gene | `CbG` | Compound binds Gene | `(:Compound)-[:BINDS]->(:Gene)` |
| Compound–causes–Side Effect | `CcSE` | Compound causes Side Effect | `(:Compound)-[:CAUSES]->(:SideEffect)` |
| Compound–downregulates–Gene | `CdG` | Compound downregulates Gene | `(:Compound)-[:DOWNREGULATES]->(:Gene)` |
| Compound–palliates–Disease | `CpD` | Compound palliates Disease | `(:Compound)-[:PALLIATES]->(:Disease)` |
| Compound–treats–Disease | `CtD` | Compound treats Disease | `(:Compound)-[:TREATS]->(:Disease)` |
| Compound–upregulates–Gene | `CuG` | Compound upregulates Gene | `(:Compound)-[:UPREGULATES]->(:Gene)` |
| Disease–associates–Gene | `DaG` | Disease associates with Gene | `(:Disease)-[:ASSOCIATES]->(:Gene)` |
| Disease–downregulates–Gene | `DdG` | Disease downregulates Gene | `(:Disease)-[:DOWNREGULATES]->(:Gene)` |
| Disease–upregulates–Gene | `DuG` | Disease upregulates Gene | `(:Disease)-[:UPREGULATES]->(:Gene)` |
| Disease–presents–Symptom | `DpS` | Disease presents Symptom | `(:Disease)-[:PRESENTS]->(:Symptom)` |
| Gene–interacts–Gene | `GiG` | Gene interacts with Gene | `(:Gene)-[:INTERACTS_WITH]->(:Gene)` |
| Gene–participates–Biological Process | `GpBP` | Gene participates in Biological Process | `(:Gene)-[:PARTICIPATES_IN]->(:BiologicalProcess)` |
| Gene–participates–Cellular Component | `GpCC` | Gene participates in Cellular Component | `(:Gene)-[:PARTICIPATES_IN]->(:CellularComponent)` |
| Gene–participates–Molecular Function | `GpMF` | Gene participates in Molecular Function | `(:Gene)-[:PARTICIPATES_IN]->(:MolecularFunction)` |
| Gene–participates–Pathway | `GpPW` | Gene participates in Pathway | `(:Gene)-[:PARTICIPATES_IN]->(:Pathway)` |
| Pharmacologic Class–includes–Compound | `PCiC` | Pharmacologic Class includes Compound | `(:PharmacologicClass)-[:INCLUDES]->(:Compound)` |


This schema serves as the foundation for implementing the HetioNet database system and is aligned with the relationship structure provided by HetioNet.
