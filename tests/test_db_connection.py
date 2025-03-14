import sys
import os
# Ensure scripts/ is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts_neo4j.db_connection import Neo4jConnection

def test_create_and_query():
    """
    Test inserting a node and retrieving it from Neo4j.
    """
    conn = Neo4jConnection()
    try:
        # Create a test node
        conn.query("CREATE (:TestNode {name: 'Test Entry'})")

        # Retrieve the test node
        result = conn.query("MATCH (n:TestNode) RETURN n.name AS name")

        # Convert result to a list and check output
        records = list(result)  
        for record in records:
            assert record["name"] == "Test Entry"
            print("Successfully created and retrieved node:", record["name"])

    except Exception as e:
        print(f"Query failed: {e}")
    finally:
        # Clean up by deleting the test node
        conn.query("MATCH (n:TestNode) DELETE n")
        conn.close()

# Run the test
if __name__ == "__main__":
    test_create_and_query()
