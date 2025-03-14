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
- [ ] **Design Document** 
  - [ ] Database design diagram
  - [ ] List of queries
  - [ ] Potential improvements (e.g., query optimization)
- [ ] **Database Implementation**
  - [ ] NoSQL database integration (at least two types)
- [ ] **Query Functionality**
  - [ ] Single-query implementation for disease-related retrieval
  - [ ] Single-query implementation for new disease treatment identification
- [ ] **Client Interface**
  - [ ] A python CLI for database creation and query.
- [ ] **Final Presentation**

## Environment Setup Guide
This guide provides a complete setup for running the project with Neo4j and Cassandra on macOS.

## Prerequisites
- Install **Homebrew**
- Install **Python 3 & pip**
- Install **Java 8 or Java 11** (Required for Cassandra)
- Install **python-dotenv** for managing environment variables automatically:
  ```bash
  pip install python-dotenv
  ```

## Install Neo4j
### **Download and Install Neo4j**
```bash
brew install neo4j
```

### **Start Neo4j**
```bash
neo4j start
```

### **Set Up Neo4j User and Password (via Terminal)**
1. Open a terminal and **start the Neo4j shell** using:
   ```bash
   cypher-shell -u neo4j -p neo4j
   ```
   - `-u` specifies the **username** (`neo4j` by default)
   - `-p` specifies the **password** (default is `neo4j`)
   
2. When prompted, change the default password:
   ```cypher
   CALL dbms.security.changeUserPassword('<your-password>');
   ```
   Replace `<your-password>` with a secure password of your choice.

3. Exit the shell:
   ```bash
   :exit
   ```

### **Create the `.env` file** (in your project root)
Create a new `.env` file and add the following lines:
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
```

### **Python Scripts Automatically Load `.env`**
You do **not** need to manually load environment variables. The project uses `python-dotenv`, which automatically reads from `.env` when running scripts.

## Install Cassandra
### **Download Cassandra**
Download the latest stable release from:
[Apache Cassandra Download](https://cassandra.apache.org/_/download.html)

### **Configuration**
- Modify settings in `conf/cassandra.yaml` as needed.
- Official documentation for setup: [Cassandra Getting Started](http://cassandra.apache.org/doc/latest/getting_started/index.html)

### **Extract and Move Cassandra**
```bash
tar -xvzf apache-cassandra-4.1.8-bin.tar
sudo mv apache-cassandra-4.1.8 /opt/cassandra
cd /opt/cassandra
```

### **Setup Environment Variables**
```bash
echo 'export CASSANDRA_HOME=/opt/cassandra' >> ~/.zshrc
echo 'export PATH=$CASSANDRA_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### **Start Cassandra**
```bash
cassandra -f  # Foreground mode
```
```bash
cassandra  # Background mode
```

### **Check Cassandra Status**
```bash
nodetool status
```
If Cassandra is running successfully, you will see `UN (Up/Normal)`.

### **Connect to Cassandra with CQL Shell**
```bash
cqlsh
```
To exit:
```bash
exit
```

### **Stop Cassandra**
```bash
pkill -f cassandra
```
```bash
nodetool drain && pkill -f cassandra
```

### **Install Cassandra Python Driver**
```bash
pip install cassandra-driver
```
Alternatively, using Conda:
```bash
conda install -c conda-forge cassandra-driver
```

### **Verify Cassandra Python Driver Installation**
```bash
python
```
Then run:
```python
import cassandra
print(cassandra.__version__)
```
Expected output:
```
3.29.2
```

## Install Required Python Packages
```bash
pip install -r requirements.txt
```

## Run Neo4j Scripts
### **Test Neo4j Connection**
```bash
python scripts_neo4j/db_connection.py
```

### **Load Data into Neo4j**
```bash
python scripts_neo4j/load_data.py
```

### **Run Queries via CLI**
```bash
python scripts_neo4j/queries.py 1 Disease::DOID:1686
```
```bash
python scripts_neo4j/queries.py 2
```

### **Run Neo4j GUI Interface**
```bash
python scripts_neo4j/gui.py
```

## Run Cassandra Implementation
### **Start Cassandra if not running**
```bash
python scripts_cassandra/hetio_cassandra.py --start
```

### **Load Data into Cassandra**
```bash
python scripts_cassandra/hetio_cassandra.py --load
```

### **Run Queries via CLI**
```bash
python scripts_cassandra/hetio_cassandra.py --query1 Disease::DOID:1686
```
```bash
python scripts_cassandra/hetio_cassandra.py --query2
```

### **Run Cassandra GUI Interface**
```bash
python scripts_cassandra/hetio_cassandra.py --gui
```

This guide provides a complete setup for running Neo4j and Cassandra on macOS.

