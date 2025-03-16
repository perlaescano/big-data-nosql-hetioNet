import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts_neo4j.db_connection import Neo4jConnection

def save_results_to_file(filename, content):
    """
    Saves query results to a file in the 'test_results' folder.
    """
    folder_path = "test_results"
    os.makedirs(folder_path, exist_ok=True)  
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Results saved to {file_path}")

# Query 1: Get Disease Information (Sorted Without APOC)
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

    WITH d, 
         [drug IN COLLECT(DISTINCT c.name) | drug] AS Drugs,
         [gene IN COLLECT(DISTINCT g.name) | gene] AS Genes,
         [location IN COLLECT(DISTINCT a.name) | location] AS Locations

    RETURN 
        d.id AS Disease_ID,
        d.name AS Disease_Name, 
        Drugs,
        Genes,
        Locations
    """
    
    conn = Neo4jConnection()
    result = conn.query(query, {"disease_id": disease_id})
    conn.close()

    if not result:
        return f"No data found for disease: {disease_id}"

    data = result[0]

    # Formatting results into a readable string
    output_text = f"\nDisease ID: {data['Disease_ID']}\n"
    output_text += f"Disease Name: {data['Disease_Name']}\n"
    output_text += f"Drugs for Treatment/Palliation: {', '.join(sorted(data['Drugs'])) if data['Drugs'] else 'None'}\n"
    output_text += f"Genes that Cause the Disease: {', '.join(sorted(data['Genes'])) if data['Genes'] else 'None'}\n"
    output_text += f"Anatomy Locations: {', '.join(sorted(data['Locations'])) if data['Locations'] else 'Unknown'}\n"

    # Save results to file
    save_results_to_file("neo4j_query1.txt", output_text)

    return output_text  # Return formatted text to GUI

# Query 2: Find New Drug Candidate
def find_new_drugs():
    """
    Identifies new drug candidates that can treat diseases but are NOT currently linked to any disease.
    """
    query = """
    MATCH (a:Anatomy)-[:AdG|AuG]->(g:Gene)  
    MATCH (c:Compound)-[:CuG|CdG]->(g)  
    WHERE 
    (NOT EXISTS { MATCH (c)-[:CtD|CpD]->(:Disease) } 
        AND EXISTS { MATCH (a)-[:AdG]->(g) } 
        AND EXISTS { MATCH (c)-[:CuG]->(g) } 
        AND EXISTS { MATCH (d:Disease)-[:DlA]->(a) })
    OR 
    (NOT EXISTS { MATCH (c)-[:CtD|CpD]->(:Disease) } 
        AND EXISTS { MATCH (a)-[:AuG]->(g) } 
        AND EXISTS { MATCH (c)-[:CdG]->(g) } 
        AND EXISTS { MATCH (d:Disease)-[:DlA]->(a) })
    
    RETURN DISTINCT c.id AS Compound_ID, c.name AS Compound_Name
    ORDER BY c.id
    """
    
    conn = Neo4jConnection()
    result = conn.query(query)
    conn.close()

    if not result:
        return "No new drug candidates found."

    # Formatting results into a readable string
    output_text = "Potential New Drugs:\n"
    output_text += "\n".join([f"{record['Compound_ID']}, Compound Name: {record['Compound_Name']}" for record in result])

    # Save results to file
    save_results_to_file("neo4j_query2.txt", output_text)

    return output_text  # Return formatted text to GUI

# Allow terminal-based queries
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts_neo4j/queries.py <query_number> [Disease_ID]")
        print("Example for disease info: python scripts_neo4j/queries.py 1 Disease::DOID:1686")
        print("Example for new drug candidates: python scripts_neo4j/queries.py 2")
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