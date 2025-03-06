import csv
import sys
import os

# Add the project root to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.db_connection import Neo4jConnection

# Set data file paths
NODES_FILE = os.path.join("data", "nodes.tsv")
EDGES_FILE = os.path.join("data", "edges.tsv")

def load_nodes(file_path):
    """
    Loads nodes from a TSV file into Neo4j.
    """
    conn = Neo4jConnection()
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        # Print headers
        print("Headers detected:", reader.fieldnames)

        for row in reader:
            print("Row being processed:", row)  
            conn.query(
                """
                MERGE (n:Entity {id: $id})
                SET n.name = $name, n.kind = $kind
                """,
                {"id": row["id"].strip(), "name": row["name"].strip(), "kind": row["kind"].strip()}
            )
    conn.close()


def load_edges(file_path):
    """
    Loads relationships from a TSV file into Neo4j.
    """
    conn = Neo4jConnection()
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        # Print headers
        print("Headers detected in edges.tsv:", reader.fieldnames)

        for row in reader:
            print("Row being processed:", row) 
            conn.query(
                """
                MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                MERGE (a)-[:RELATIONSHIP {type: $metaedge}]->(b)
                """,
                {"source": row["source"].strip(), "target": row["target"].strip(), "metaedge": row["metaedge"].strip()}
            )
    conn.close()


if __name__ == "__main__":
    print("Loading nodes from:", NODES_FILE)
    load_nodes(NODES_FILE)
    print("Nodes loaded successfully.")

    print("Loading edges from:", EDGES_FILE)
    load_edges(EDGES_FILE)
    print("Edges loaded successfully.")
