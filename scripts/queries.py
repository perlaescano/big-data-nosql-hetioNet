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
        d.id AS Disease_ID,
        d.name AS Disease_Name, 
        COLLECT(DISTINCT c) AS Drugs, 
        COLLECT(DISTINCT g.name) AS Genes, 
        COLLECT(DISTINCT a.name) AS Locations
    """
    
    conn = Neo4jConnection()
    result = conn.query(query, {"disease_id": disease_id})
    conn.close()

    # Process results
    if result:
        data = result[0]
        print(f"\n{data['Disease_ID']}")
        print(f"Disease Name: {data['Disease_Name']}")
        
        # Format drugs list
        if data['Drugs']:
            sorted_drugs = sorted(data['Drugs'], key=lambda x: x['id'])  # Sort alphabetically by ID
            drug_output = f"{', '.join([d['name'] for d in sorted_drugs])}"
        else:
            drug_output = "None"
        print(f"Drugs for Treatment/Palliation: {drug_output}")

        # Format genes
        sorted_genes = sorted(data['Genes']) if data['Genes'] else []
        print(f"Genes that Cause the Disease: {', '.join(sorted_genes) if sorted_genes else 'None'}")

        # Format locations
        sorted_locations = sorted(data['Locations']) if data['Locations'] else []
        print(f"Anatomy Locations: {', '.join(sorted_locations) if sorted_locations else 'Unknown'}\n")
    else:
        print("No data found for the given disease ID.")

# Query 2: Find New Drug Candidate
def find_new_drugs():
    """
    Identifies new drug candidates that can treat diseases but are NOT currently linked to any disease.
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
    RETURN DISTINCT c.id AS Compound_ID, c.name AS Compound_Name
    ORDER BY c.id
    """
    
    conn = Neo4jConnection()
    result = conn.query(query)
    conn.close()

    # Process and display results 
    if result:
        print("\nPotential New Drugs:")
        for record in result:
            print(f"{record['Compound_ID']}, Compound Name: {record['Compound_Name']}")
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