import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.db_connection import Neo4jConnection

# DB Answers Part 1
def get_disease_info(disease_id):
    """
    Given a disease ID, retrieve:
    1. Disease name
    2. Drug names that treat (CtD) or palliate (CpD) the disease
    3. Gene names associated with the disease (DaG, DdG, DuG)
    4. Where the disease occurs (linked via DlA)
    """
    query = """
    MATCH (d:Disease {id: $disease_id})
    OPTIONAL MATCH (d)<-[:CtD|CpD]-(c:Compound)  // Compounds treating or palliating the disease
    OPTIONAL MATCH (d)-[:DaG|DdG|DuG]->(g:Gene)  // Genes associated with the disease
    OPTIONAL MATCH (d)-[:DlA]->(a:Anatomy)       // Where the disease occurs (anatomy)
    RETURN 
        d.name AS Disease_Name, 
        COLLECT(DISTINCT c.name) AS Drugs, 
        COLLECT(DISTINCT g.name) AS Genes, 
        COLLECT(DISTINCT a.name) AS Locations
    """
    
    conn = Neo4jConnection()
    result = conn.query(query, {"disease_id": disease_id})
    conn.close()

    # Extract data from query result
    if result:
        data = result[0]
        print(f"\nDisease Name: {data['Disease_Name']}")
        print(f"Drugs that treat/palliate: {', '.join(data['Drugs']) if data['Drugs'] else 'None'}")
        print(f"Associated Genes: {', '.join(data['Genes']) if data['Genes'] else 'None'}")
        print(f"Occurs in: {', '.join(data['Locations']) if data['Locations'] else 'Unknown'}\n")
    else:
        print("No data found for the given disease ID.")

# Allow terminal-based queries
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/queries.py <Disease_ID>")
        sys.exit(1)
    
    disease_id = sys.argv[1]
    get_disease_info(disease_id)
