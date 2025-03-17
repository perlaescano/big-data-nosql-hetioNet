# CSCI 79525 - Big Data Project 1: HetioNet Database System

## Project Overview
Build a database system to model **HetioNet**. 

## Requirements
- Implement a **Python command-line client** for database creation and queries.
- Utilize **at least two types of NoSQL stores** (Document, Graph, Key-value, Column Family).
- Ensure **quick response time** for queries.
- Implement the database to answer the following queries in a **single query**:
  1. Given a disease ID, retrieve:
     - The disease name.
     - Drug names that can treat or palliate the disease.
     - Gene names associated with the disease.
     - The locations where the disease occurs.
  2. Identify compounds that can treat a **new disease** by analyzing up-regulation and down-regulation relationships. Obtain and output all drugs in a **single query**.

## Data Files
The dataset includes:
- **nodes.tsv** (Entities like genes, diseases, compounds)
- **edges.tsv** (Relationships between entities)

## Project Deliverables
- **Design Document** 
  - Database design diagram
  -  List of queries
  -  Potential improvements (e.g., query optimization)
- **Database Implementation**
  -  NoSQL database integration (at least two types)
-  **Query Functionality**
  -  Single-query implementation for disease-related retrieval
  -  Single-query implementation for new disease treatment identification
- **Client Interface**
  -  A python CLI for database creation and query.
-  **Final Presentation**

## Prerequisites
- Install **Homebrew**
- Install **Python 3 & pip**
- Install **python-dotenv** 
- Install **Neo4j**
- Install **Cassandra**

