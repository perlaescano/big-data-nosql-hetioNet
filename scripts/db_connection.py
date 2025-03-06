import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Neo4j credentials from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Neo4j Connection Class
class Neo4jConnection:
    """
    A class to manage Neo4j database connections and execute queries.
    """

    def __init__(self):
        """
        Initializes the Neo4j driver with the provided credentials.
        """
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def query(self, query, parameters=None):
        """
        Executes a Cypher query and returns the results as a list.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of query parameters.
        :return: A list of records from the query result.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return list(result)  # Convert result to a list before returning

    def close(self):
        """
        Closes the Neo4j database connection.
        """
        self.driver.close()

# Test connection when running the script directly
if __name__ == "__main__":
    conn = Neo4jConnection()
    try:
        result = conn.query("RETURN 'Test Connection' AS message")  # Test query to check connection
        for record in result:
            print("Successfully connected to Neo4j:", record["message"])
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
    finally:
        conn.close()
