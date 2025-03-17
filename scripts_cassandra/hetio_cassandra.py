import subprocess
import time
import sys
import os
import csv
from cassandra.cluster import Cluster
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

CASSANDRA_PATH = "/opt/cassandra/bin/cassandra"

EDGE_DATA_FILE = "../data/edges.tsv"
NODE_DATA_FILE = "../data/nodes.tsv"

################################################################################################
# Cassandra setup
################################################################################################
def is_cassandra_running():
    """Check if Cassandra is already running by using nodetool status."""
    try:
        result = subprocess.run(["nodetool", "status"], capture_output=True, text=True)
        if "UN" in result.stdout:  # 'UN': Up and Normal
            print("[✔] Cassandra is already running!")
            return True
    except Exception:
        pass  # If nodetool fails, Cassandra is not running
    print("[❌] Cassandra is NOT running.")
    return False

def start_cassandra():
    """Starts Cassandra manually from the installation directory."""
    try:
        subprocess.Popen([CASSANDRA_PATH, "-f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[✔] Cassandra is starting...")

        # Wait for Cassandra to initialize
        time.sleep(15)
    except Exception as e:
        print("[✖] Error starting Cassandra: {e}")

def stop_cassandra():
    os.system("pkill -f cassandra")
    print("[✔] Cassandra service stopped.")

def connect_to_cassandra():
    """Connects to Cassandra."""
    try:
        cluster = Cluster(["127.0.0.1"])
        session = cluster.connect()
        print("[✔] Connected to Cassandra successfully!")
        return session
    except Exception as e:
        print(f"[✖] Connection failed: {e}")
        return None

################################################################################################
# Cassandra DB operations: Create keyspace, Create table and Add data for Hetio
################################################################################################
def create_keyspace(session):
    """Create Keyspace if not exists."""
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS hetio_db 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    
    session.set_keyspace("hetio_db")
    print("[✔] Keyspace 'hetio_db' is set successfully!")

def create_disease_table(session):
    """Create the disease_info table for query 1."""

    session.execute("""
        CREATE TABLE IF NOT EXISTS disease_info (
            disease_id TEXT PRIMARY KEY,
            disease_name TEXT,
            drug_names SET<TEXT>,
            gene_names SET<TEXT>,
            location_names SET<TEXT>
        );
    """)
    print("[✔] disease_info table created.")

def insert_disease_info(session, disease_names, drugs_names, gene_names, location_names, disease_data):
    """Insert collected data into Cassandra."""
    for disease_id, data in disease_data.items():
        disease_name = disease_names.get(disease_id, "Unknown Disease")
        drugs = {drugs_names.get(x,x) for x in data["drugs"]}
        genes = {gene_names.get(x,x) for x in data["genes"]}
        locations = {location_names.get(x,x) for x in data["locations"]}

        session.execute("""
            INSERT INTO disease_info (disease_id, disease_name, drug_names, gene_names, location_names) 
            VALUES (%s, %s, %s, %s, %s);
        """, (disease_id, disease_name, drugs, genes, locations))
    
    print("[✔] Disease data inserted successfully!")

def create_compound_table(session):
    """ Create the compound_info table for query 2."""
    session.execute("""
        CREATE TABLE IF NOT EXISTS compound_info (
            compound_id TEXT PRIMARY KEY,
            compound_name TEXT,
            is_connected_with_disease BOOLEAN
        );
    """)
    print("[✔] compound_info table created.")

def insert_compounds_info(session, drugs_names, new_drugs_info, old_drugs_info):
    """Insert collected data into Cassandra"""
    for compound_id in new_drugs_info:
        session.execute("""
            INSERT INTO compound_info (compound_id, compound_name, is_connected_with_disease) 
            VALUES (%s, %s, %s);
        """, (compound_id, drugs_names[compound_id], False))

    for compound_id in old_drugs_info:
        session.execute("""
            INSERT INTO compound_info (compound_id, compound_name, is_connected_with_disease) 
            VALUES (%s, %s, %s);
        """, (compound_id, drugs_names[compound_id], True))

    print("[✔] Compound data inserted successfully!")

################################################################################################
# Load Hetio data
################################################################################################
def load_disease_names(filename=NODE_DATA_FILE):
    """Load nodes.tsv to get disease names."""
    disease_names = {}
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            node_id, name, kind = row
            if "Disease::" in node_id:      # Identify diseases
                disease_names[node_id] = name
    return disease_names

def load_drugs_names(filename=NODE_DATA_FILE):
    """Load nodes.tsv to get Compound names."""
    compound_names = {}
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            node_id, name, kind = row
            if "Compound::" in node_id:     # Identify drugs
                compound_names[node_id] = name
    return compound_names

def load_gene_names(filename=NODE_DATA_FILE):
    """Load nodes.tsv to get Gene names."""
    gene_names = {}
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            node_id, name, kind = row
            if "Gene::" in node_id:              # Identify gene
                gene_names[node_id] = name
    return gene_names

def load_nodes_information(filename=NODE_DATA_FILE):
    """Load nodes.tsv to get disease names."""
    disease_names = {}
    compound_names = {}
    gene_names = {}
    location_names = {}
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            node_id, name, kind = row
            if "Disease::" in node_id:          # Identify diseases
                disease_names[node_id] = name
            elif "Compound::" in node_id:       # Identify drugs
                compound_names[node_id] = name
            elif "Gene::" in node_id:           # Identify gene
                gene_names[node_id] = name
            elif "Anatomy::" in node_id:        # Identify location (anatomy)
                location_names[node_id] = name    

    return (disease_names, compound_names, gene_names, location_names)

def load_disease_relations(filename=EDGE_DATA_FILE):
    """Load edges.tsv to map diseases to drugs, genes, and locations."""
    disease_data = defaultdict(lambda: {"drugs": set(), "genes": set(), "locations": set()})
    
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            source, metaedge, target = row
            #print(source, metaedge, target)
            if "Disease::" in target:
                if metaedge == "CtD":  # Compound-treats-Disease
                    disease_data[target]["drugs"].add(source)
                elif metaedge == "CpD":  # Compound-Palliate-Disease
                    disease_data[target]["drugs"].add(source)

            if "Disease::" in source:
                if metaedge == "DuG":  # Disease-upregulated-Gene
                    disease_data[source]["genes"].add(target)
                elif metaedge == "DdG":  # Disease-upregulated-Gene
                    disease_data[source]["genes"].add(target)
                elif metaedge == "DaG":  # Disease-upregulated-Gene
                    disease_data[source]["genes"].add(target)
                elif metaedge == "DlA":  # Disease-localized-in-Anatomy
                    disease_data[source]["locations"].add(target)

    for disease_id, data in disease_data.items():
        data["drugs"] = sorted(data["drugs"])
        data["genes"] = sorted(data["genes"])
        data["locations"] = sorted(data["locations"])

    return disease_data

def load_compound_gene_anatomy_relations(filename=EDGE_DATA_FILE):
    """Load edges.tsv to get compound gene anatomy link"""
    Compound_CdG = defaultdict(list)
    Compound_CuG = defaultdict(list)
    Anatomy_AdG = defaultdict(list)
    Anatomy_AuG = defaultdict(list)

    info_data = set()

    # gene is key
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            source, metaedge, target = row
            #print(source, metaedge, target)
            if "Compound::" in source and "CdG" in metaedge and "Gene::" in target:
                Compound_CdG[target].append(source) 
            elif "Compound::" in source and "CuG" in metaedge and "Gene::" in target:
                Compound_CuG[target].append(source)
            elif "Anatomy::" in source and "AdG" in metaedge and "Gene::" in target:
                Anatomy_AdG[target].append(source)
            elif "Anatomy::" in source and "AuG" in metaedge and "Gene::" in target:
                Anatomy_AuG[target].append(source)

    for gene_id, compound_id_list in Compound_CdG.items():
        for compound_id in compound_id_list:
            anatomy_id_list = Anatomy_AuG.get(gene_id)
            if anatomy_id_list is not None:
                for anatomy_id in anatomy_id_list:
                    info_data.add((gene_id, compound_id, anatomy_id))
                    #print(gene_id, compound_id, anatomy_id) 
            
    for gene_id, compound_id_list in Compound_CuG.items():
        for compound_id in compound_id_list:
            anatomy_id_list = Anatomy_AdG.get(gene_id)
            if anatomy_id_list is not None:
                for anatomy_id in anatomy_id_list:
                    info_data.add((gene_id, compound_id, anatomy_id))
                    #print(gene_id, compound_id, anatomy_id) 

    #print("Path count: ", len(info_data))

    return info_data

def load_anatomy_desease_compound_relations(filename=EDGE_DATA_FILE):
    """Load edges.tsv to disease and anatomy"""
    disease_data = defaultdict(lambda: {"drugs": set(), "genes": set(), "locations": set()})
    
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            source, metaedge, target = row
            #print(source, metaedge, target)
            if "Anatomy::" in target:
                if metaedge == "DlA":  
                    disease_data[source]["locations"].add(target)

            if "Compound::" in source:
                if metaedge == "CtD" or metaedge == "CpD":  
                    disease_data[target]["drugs"].add(source)
            
            if "Gene::" in target:
                if metaedge == "DuG" or metaedge == "DaG" or metaedge == "DdG":
                    disease_data[source]["genes"].add(target)
        
    return disease_data    

def load_new_drugs_info(compound_gene_anatomy_relations, anatomy_disease_compound_relations):
    """Insert collected data into Cassandra"""
    all_drugs_info = set()
    old_drugs_info = set()
    for item in compound_gene_anatomy_relations:
        # item[0] gene
        # item[1] compound, drug
        # item[2] Anatomy        
        for disease_id, data in anatomy_disease_compound_relations.items():
            all_drugs_info.add(item[1])
            if item[1] in data["drugs"]:
                old_drugs_info.add(item[1])
    
    new_drugs_info = all_drugs_info.difference(old_drugs_info)

    return (new_drugs_info, old_drugs_info)

################################################################################################
# Queries
################################################################################################
def query_disease_info(session, disease_id):
    """Query disease information."""
    rows = session.execute("SELECT * FROM disease_info WHERE disease_id = %s", [disease_id])

    output_lines = []
    for row in rows:
        output_lines.append(f"Disease ID: {row.disease_id}")
        output_lines.append(f"Disease Name: {row.disease_name}")

        # Use join() for cleaner concatenation
        output_lines.append(f"Drugs for Treatment/Palliation: {', '.join(row.drug_names) if row.drug_names else ' '}")
        output_lines.append(f"Genes that Cause the Disease: {', '.join(row.gene_names) if row.gene_names else ' '}")
        output_lines.append(f"Anatomy Locations: {', '.join(row.location_names) if row.location_names else ' '}")

    return '\n'.join(output_lines)

def query_all_disease_info(session):
    """Query all disease information."""
    rows = session.execute("SELECT * FROM disease_info")
    output_lines = ""
    for row in rows:
        output_lines += f"{row.disease_id}, Disease Name: {row.disease_name}, Drugs: {row.drug_names}\n"
    return rows

def query_all_new_compounds_info(session):
    rows = session.execute("SELECT compound_id, compound_name FROM compound_info WHERE is_connected_with_disease = %s ALLOW FILTERING", [False])

    sorted_rows = sorted(rows, key=lambda row: row.compound_id)
    output_lines = ""
    for row in sorted_rows:
        output_lines += f"{row.compound_id}, Compound Name: {row.compound_name}\n"
        
    return output_lines

################################################################################################
# Save result to file
################################################################################################
def save_results_to_file(filename, content):
    """Saves query results to a file in the 'test_results' folder."""
    folder_path = "../test_results"
    os.makedirs(folder_path, exist_ok=True)  
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"[✔] Query results saved to {file_path}")

################################################################################################
# Connection with GUI
################################################################################################
def get_result_query1(disease_id):
    print("[✔] Query 1 is called.")

    if not is_cassandra_running():
        start_cassandra()
    session = connect_to_cassandra()

    create_keyspace(session)
    create_disease_table(session)

    (disease_names, drugs_names, gene_names, location_names) = load_nodes_information(NODE_DATA_FILE)
    disease_relations = load_disease_relations(EDGE_DATA_FILE)

    insert_disease_info(session, disease_names, drugs_names, gene_names, location_names, disease_relations)

    # Query execute for a specific disease
    # Disease::DOID:263
    # Disease::DOID:0050742
    output_text = query_disease_info(session, disease_id)

    # Save results to file
    save_results_to_file("cassandra_query1.txt", output_text)

    return output_text

def get_result_query2():
    print("[✔] Query 2 is called.")
    if not is_cassandra_running():
        start_cassandra()
    session = connect_to_cassandra()

    create_keyspace(session)
    create_compound_table(session)
    
    (disease_names, drugs_names, gene_names, location_names) = load_nodes_information(NODE_DATA_FILE)
    compound_gene_anatomy_relations = load_compound_gene_anatomy_relations(EDGE_DATA_FILE)
    anatomy_disease_compound_relations = load_anatomy_desease_compound_relations(EDGE_DATA_FILE)
    (new_drugs_info, old_drugs_info) = load_new_drugs_info(compound_gene_anatomy_relations, anatomy_disease_compound_relations)

    insert_compounds_info(session, drugs_names, new_drugs_info, old_drugs_info)

    # Query execute
    output_text = query_all_new_compounds_info(session)

    # Save results to file
    save_results_to_file("cassandra_query2.txt", output_text)

    return output_text

################################################################################################
# GUI
################################################################################################
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hetio Data Analysis on Cassandra Database")
        self.geometry("700x600")
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.pages = {}
        for Page in (InitPage, Query1Page, Query2Page):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.grid(row=0, column=0, sticky="nsew")
        
        self.show_page(InitPage)
    
    def show_page(self, page_class):
        page = self.pages[page_class]
        page.tkraise()

class InitPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Centering Frame for Buttons
        center_frame = tk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')  # Center the frame
        center_frame.pack(expand=True)

        text_query1 = ("Query 1\n"
            "   Given a disease id, what is its name,\n"
            "   what are drug names that can treat or palliate this disease,\n"
            "   what are gene names that cause this disease, and\n"
            "   where this disease occurs?\n"
            "   Obtain and output this information in a single query.")

        text_query2 = ("Query 2\n"
            "   We assume that a compound can treat a disease \n"
            "   if the compound up-regulates/down-regulates a gene, \n"
            "   but the location down-regulates/up-regulates the gene \n"
            "   in an opposite direction where the disease occurs. \n"
            "   Find all compounds that can treat a new disease \n"
            "   (i.e. the missing edges between compound and disease excluding existing drugs). \n"
            "   Obtain and output all drugs in a single query.")

        text_test = "Hello"

        button1 = tk.Button(center_frame, text=text_query1, width=70, height=8, anchor='nw', justify='left', 
                            command=lambda: controller.show_page(Query1Page), font=("Arial", 14))
        button1.pack(padx=30, pady=20)

        button2 = tk.Button(center_frame, text=text_query2, width=70, height=8, anchor='nw', justify='left',  
                            command=lambda: controller.show_page(Query2Page), font=("Arial", 14))
        button2.pack(padx=30, pady=20)

class Query1Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Enter the disease id", font=("Arial", 14))
        label.pack(padx=30, pady=10)
        
        # Entry widget for user input
        self.entry = tk.Entry(self, font=("Arial", 14))
        self.entry.pack(padx=30, pady=10)

        # Button to get the input and display it
        button1 = tk.Button(self, text="Execute Query 1", command=self.get_query_result, font=("Arial", 14))
        button1.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_page(InitPage), font=("Arial", 14))
        button2.pack(padx=30, pady=10)
        
        # Create Text widget for displaying content
        self.text_widget = tk.Text(self, wrap="word", font=("Arial", 14), padx=10, pady=10)
        self.text_widget.config(state="disabled")  # Disable editing initially

        # Create Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Grid layout
        self.text_widget.pack(side="left", expand=True, fill="both", pady=10)
        scrollbar.pack(side="right", fill="y")

        # Configure expansion
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def get_query_result(self):
        user_text = self.entry.get()  # Get the text entered by the user
        output_text = ""
        if "Disease::" in user_text:  
            output_text = get_result_query1(user_text)
        else:
            print("Wrong disease id")

        # Enable text widget to insert new content
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)  # Clear existing text
        self.text_widget.insert("1.0", output_text)  # Insert new text
        self.text_widget.config(state="disabled")  # Disable editing again
        
class Query2Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Button to get the input and display it
        button1 = tk.Button(self, text="Execute Query 2", command=self.get_query_result, font=("Arial", 14))
        button1.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_page(InitPage), font=("Arial", 14))
        button2.pack(padx=30, pady=10)

        # Create Text widget for displaying content
        self.text_widget = tk.Text(self, wrap="word", font=("Arial", 14), padx=10, pady=10)
        self.text_widget.config(state="disabled")  # Disable editing initially

        # Create Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Grid layout
        #self.text_widget.grid(row=0, column=0, sticky="nsew")
        #scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.pack(side="left", expand=True, fill="both", pady=10)
        scrollbar.pack(side="right", fill="y")

        # Configure expansion
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def get_query_result(self):
        output_text = get_result_query2()       

        # Enable text widget to insert new content
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)  # Clear existing text
        self.text_widget.insert("1.0", output_text)  # Insert new text
        self.text_widget.config(state="disabled")  # Disable editing again
 
        return

if __name__ == "__main__": 
    app = App()
    app.mainloop()