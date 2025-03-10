import csv
import sys
import os

# Add the project root to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.db_connection import Neo4jConnection

# Set data file paths
NODES_FILE = os.path.join("data", "nodes.tsv")
EDGES_FILE = os.path.join("data", "edges.tsv")

# Function to determine correspondent node label based on kind
def get_node_label(kind):
    """ Maps 'kind' from nodes.tsv to the correct Neo4j label. """
    label_mapping = {
        "Compound": "Compound",
        "Disease": "Disease",
        "Gene": "Gene",
        "Anatomy": "Anatomy"
    }
    return label_mapping.get(kind, "Entity")  # Default to Entity if kind is unknown

# Function to convert `>` to `_` in relationship names
def convert_relationship_type(metaedge):
    """ Converts `>` to `_` in relationship types for Neo4j compatibility. """
    return metaedge.replace(">", "_")

def load_nodes(file_path):
    """
    Loads nodes from a TSV file into Neo4j with labels.
    """
    conn = Neo4jConnection()
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        print("Headers detected:", reader.fieldnames)  

        for row in reader:
            label = get_node_label(row["kind"].strip())
            print(f"Creating node: {row['id']} [{label}]")

            conn.query(
                f"""
                MERGE (n:{label} {{id: $id}})
                SET n.name = $name
                """,
                {"id": row["id"].strip(), "name": row["name"].strip()}
            )
    conn.close()

def load_edges(file_path):
    """
    Loads all relationships from a TSV file into Neo4j without duplicates.
    Prints progress every 10,000 edges.
    """
    conn = Neo4jConnection()
    count = 0  
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            original_metaedge = row["metaedge"].strip()  # Keep the original
            relationship_type = convert_relationship_type(original_metaedge)  # Convert for Neo4j

            conn.query(
                f"""
                MATCH (a {{id: $source}}), (b {{id: $target}})
                MERGE (a)-[r:{relationship_type}]->(b)
                ON CREATE SET r.metaedge = $original_metaedge, r.created_at = timestamp()
                """,
                {"source": row["source"].strip(), "target": row["target"].strip(), "original_metaedge": original_metaedge}
            )

            count += 1
            if count % 10000 == 0:
                print(f"{count} edges processed...")

    print(f"Finished loading {count} edges.")
    conn.close()


if __name__ == "__main__":
    print("Loading nodes from:", NODES_FILE)
    load_nodes(NODES_FILE)
    print("Nodes loaded successfully.")

    print("Loading all edges...")
    load_edges(EDGES_FILE)  
    print("All edges loaded successfully.")
