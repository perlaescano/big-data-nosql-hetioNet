# Environment Setup Guide
<pre>
Prerequisites
    – Install Java 8 or Java 11
Download Cassandra
    – https://cassandra.apache.org/_/download.html
Configuration
    – In conf/cassandra.yaml
Getting started
    – http://cassandra.apache.org/doc/latest/getting_started/index.html
Python Driver (DataStax Cassandra Driver)
    – https://docs.datastax.com/en/developer/python-driver/
</pre>
    
# Detail steps for setup (Based on MacOS)
<pre>
1. Download, extract and move Cassandra
Download the latest stable release: apache-cassandra-4.1.8-bin.tar
Extract: tar -xvzf apache-cassandra-4.1.8-bin.tar
Move the extracted folder to a permanent location: ex sudo mv apache-cassandra-4.1.8 /opt/cassandra
Nevigate to the Cassandra directory

2. Setup environment variables
Open your shell configuration file: sudo nano ~/.zshrc
Add the following lines at the bottom:
export CASSANDRA_HOME=/opt/cassandra
export PATH=$CASSANDRA_HOME/bin:$PATH
Save and exit
Reload the terminal configuration: source ~/.zshrc

3. Start Cassandra
study_cassandra % cassandra -f (foreground)
study_cassandra % cassandra (background)
nodetool status (check if Cassandra is running): If you see UN(Up/Normal), Cassandra is running successfully

study_cassandra % nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address    Load       Tokens  Owns (effective)  Host ID                               Rack 
UN  127.0.0.1  75.75 KiB  16      100.0%            c0ed76ed-ae82-46da-a767-e14d6269fa60  rack1

4. Connect to Cassandra by CQL shell (Cassandra Query Language shell) to interact with the database
study_cassandra % cqlsh
Connected to Test Cluster at 127.0.0.1:9042
[cqlsh 6.1.0 | Cassandra 4.1.8 | CQL spec 3.4.6 | Native protocol v5]
Use HELP for help.
cqlsh> exit

5. Stop Cassandra
study_cassandra % pkill -f cassandra 
or
study_cassandra % nodetool drain && pkill -f cassandra

6. Install the Cassandra Python Driver
study_cassandra % pip install cassandra-driver
or
study_cassandra % conda install -c conda-forge cassandra-driver

7. Verify the Python Driver installation
study_cassandra % python                     
Python 3.9.21 | packaged by conda-forge | (main, Dec  5 2024, 13:47:18) 
[Clang 18.1.8 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import cassandra
>>> print(cassandra.__version__)
3.29.2
>>> 
</pre>

# Run python script (python 3.9, tkinter 8.6)
<pre>
1. Run python script for GUI:
study_cassandra % python hetio_cassandra.py
2. Result file:
Test result files (cassandra_query1.txt and cassandra_query2.txt) will be stored under test_results directory
</pre>

<img width="812" alt="cassandra_1" src=pictures/cassandra_1.png />
<img width="812" alt="cassandra_2" src=pictures/cassandra_2.png />
<img width="812" alt="cassandra_3" src=pictures/cassandra_3.png />

# Design diagram
<img width="812" alt="cassandra_4" src=pictures/cassandra_4.png />

# Cassandra database for HetioNet
<pre>
1. HetioNet
node data: nodes.tsv
edge data: edges.tsv

2. keyspace: hetio_db
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS hetio_db 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

3. tables: 
disease_info
    session.execute("""
        CREATE TABLE IF NOT EXISTS disease_info (
            disease_id TEXT PRIMARY KEY,
            disease_name TEXT,
            drug_names SET<TEXT>,
            gene_names SET<TEXT>,
            location_names SET<TEXT>
        );
    """)

    session.execute("""
            INSERT INTO disease_info (disease_id, disease_name, drug_names, gene_names, location_names) 
            VALUES (%s, %s, %s, %s, %s);
        """, (disease_id, disease_name, drugs, genes, locations))

compound_info
    session.execute("""
        CREATE TABLE IF NOT EXISTS compound_info (
            compound_id TEXT PRIMARY KEY,
            compound_name TEXT,
            is_connected_with_disease BOOLEAN
        );
    """) 

    session.execute("""
            INSERT INTO compound_info (compound_id, compound_name, is_connected_with_disease) 
            VALUES (%s, %s, %s);
        """, (compound_id, drugs_names[compound_id], False))
    session.execute("""
            INSERT INTO compound_info (compound_id, compound_name, is_connected_with_disease) 
            VALUES (%s, %s, %s);
        """, (compound_id, drugs_names[compound_id], True))

</pre>

# Queries for Cassandra
<pre>
Query 1:
    Given a disease id, what is its name,
    what are drug names that can treat or palliate this disease,
    what are gene names that cause this disease, and
    where this disease occurs?
    Obtain and output this information in a single query.

    session.execute("SELECT * FROM disease_info WHERE disease_id = %s", [disease_id])

Query 2:
    We assume that a compound can treat a disease
    if the compound up-regulates/down-regulates a gene, 
    but the location down-regulates/up-regulates the gene 
    in an opposite direction where the disease occurs. 
    Find all compounds that can treat a new disease 
    (i.e. the missing edges between compound and disease excluding existing drugs). 
    Obtain and output all drugs in a single query.

    session.execute("SELECT compound_id, compound_name FROM compound_info WHERE is_connected_with_disease = %s ALLOW FILTERING", [False])

</pre>

# Potential improvement
<pre>
1. Since Cassandra does not support joins, we use pre-processing functions with basic Python data structures like lists and sets. 
This could be improved by utilizing Pandas' merge function for more efficient joins.
See test_alternative_approach_with_pandas.py under test directory.
2. The current column family (table) structure is simple and optimized for two specific queries. 
By storing a Pandas DataFrame after joining edge and node information, we could create a more flexible and generic table structure.
3. We will explore alternative methods that reduce dependency on Python.
</pre>
