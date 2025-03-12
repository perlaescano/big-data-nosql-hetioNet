import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.db_connection import Neo4jConnection

# Query 1: Get Disease Information
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

# Query 2: Find New Drug Candidate
def find_new_drugs():
    """
    Identifies compounds that can treat diseases based on gene regulation patterns:
    - The compound up-regulates (`CuG`) or down-regulates (`CdG`) a gene.
    - The location of the disease (Anatomy) down-regulates (`AdG`) or up-regulates (`AuG`) the same gene in the opposite direction.
    - The compound is NOT already linked to any disease (`CtD`).
    """
    query = """
    MATCH (a:Anatomy)-[:AdG|AuG]->(g:Gene)  // Anatomy up/down-regulates gene
    MATCH (c:Compound)-[:CuG|CdG]->(g)  // Compound up/down-regulates the same gene
    WHERE NOT EXISTS {
        MATCH (c)-[:CtD]->(:Disease)  // Ensure the compound is NOT already linked to any disease
    }
    RETURN DISTINCT c.name AS Potential_Drug
    """
    
    conn = Neo4jConnection()
    result = conn.query(query)
    conn.close()

    # Process and display results 
    if result:
        drugs = [record["Potential_Drug"] for record in result]
        print(f"\nPotential New Drugs: {', '.join(drugs) if drugs else 'None Found'}\n")
    else:
        print("No new drug candidates found.")

# Allow terminal-based queries
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/queries.py <query_number> [Disease_ID]")
        print("Example for disease info: python scripts/queries.py 1 Disease::DOID:1686")
        print("Example for new drug candidates: python scripts/queries.py 2")
        sys.exit(1)
    
    query_number = sys.argv[1]
    if query_number == "1":
        if len(sys.argv) != 3:
            print("For Query 1, please provide a disease ID.")
            sys.exit(1)
        disease_id = sys.argv[2]
        get_disease_info(disease_id)
    elif query_number == "2":
        find_new_drugs()
    else:
        print("Invalid query number. Use 1 for disease info, 2 for new drug candidates.")