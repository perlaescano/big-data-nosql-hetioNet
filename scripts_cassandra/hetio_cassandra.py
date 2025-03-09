import subprocess
import time
import csv
from cassandra.cluster import Cluster
from collections import defaultdict
import tkinter as tk
from tkinter import ttk

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

# Query 1
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

# Query 2
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

def insert_compounds_info(session, drugs_names, new_drugs_info):
    """Insert collected data into Cassandra"""
    for compound_id in new_drugs_info:
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

# Query 1
def load_disease_relations(filename=EDGE_DATA_FILE):
    """Load edges.tsv to map diseases to drugs, genes, and locations."""
    disease_data = defaultdict(lambda: {"drugs": set(), "genes": set(), "locations": set()})
    
    #print("Taly: Let make table!")
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            source, metaedge, target = row
            #print(source, metaedge, target)
            if "Disease::" in target:
                if metaedge == "CtD":  # Compound-treats-Disease
                    disease_data[target]["drugs"].add(source)
                    #print("Taly 1")
                elif metaedge == "CpD":  # Compound-Palliate-Disease
                    disease_data[target]["drugs"].add(source)
                    #print("Taly 2")

            if "Disease::" in source:
                if metaedge == "DuG":  # Disease-upregulated-Gene
                    disease_data[source]["genes"].add(target)
                    #print("Taly 3")
                elif metaedge == "DlA":  # Disease-localized-in-Anatomy
                    disease_data[source]["locations"].add(target)
                    #print("Taly 4")    
        
    return disease_data

# Query 2
def load_compound_gene_anatomy_relations(filename=EDGE_DATA_FILE):
    """Load edges.tsv to get compound gene anatomy link"""
    Compound_CdG = defaultdict()
    Compound_CuG = defaultdict()
    Anatomy_AdG = defaultdict()
    Anatomy_AuG = defaultdict()

    info_data = set()

    #print("Taly: Let make table!")
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            source, metaedge, target = row
            #print(source, metaedge, target)
            if "Compound::" in source and "CdG" in metaedge and "Gene::" in target:
                Compound_CdG[target] = source 
            elif "Compound::" in source and "CuG" in metaedge and "Gene::" in target:
                Compound_CuG[target] = source
            elif "Anatomy::" in source and "AdG" in metaedge and "Gene::" in target:
                Anatomy_AdG[target] = source
            elif "Anatomy::" in source and "AuG" in metaedge and "Gene::" in target:
                Anatomy_AuG[target] = source

        for gene_id, compound_id in Compound_CdG.items():
            anatomy_id = Anatomy_AuG.get(gene_id)
            if anatomy_id is not None:
                info_data.add((gene_id, compound_id, anatomy_id))
                #print(gene_id, compound_id, anatomy_id) 

        for gene_id, compound_id in Compound_CuG.items():
            anatomy_id = Anatomy_AdG.get(gene_id)
            if anatomy_id is not None:
                info_data.add((gene_id, compound_id, anatomy_id))
                #print(gene_id, compound_id, anatomy_id) 
    
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
                    #print("Taly 1: disease relationship", source, " : ", disease_data[source])

            if "Compound::" in source:
                if metaedge == "CtD" or metaedge == "CpD":  
                    disease_data[target]["drugs"].add(source)
                    #print("Taly 2: disease relationship", target, " : ", disease_data[target])
        
    #print("Taly: disease relationship", disease_data)
    return disease_data

def load_new_drugs_info(compound_gene_anatomy_relations, anatomy_disease_compound_relations):
    """Insert collected data into Cassandra"""
    all_drugs_info = set()
    old_drugs_info = set()
    for item in compound_gene_anatomy_relations:
        # item[0] gene
        # item[1] compound, drug
        # item[2] Anatomy        
        #print("Taly: compound gen anatomy :", item[0], item[1], item[2])
        for disease_id, data in anatomy_disease_compound_relations.items():
            #print("Taly: disease_id, data:", disease_id, data)
            all_drugs_info.add(item[1])
            if item[1] in data["drugs"] and item[2] in data["locations"]:
                old_drugs_info.add(item[1])

    #print("Taly: all drug info:", len(all_drugs_info), all_drugs_info)
    #print("Taly: old drug info:", len(old_drugs_info), old_drugs_info)
    
    new_drugs_info = all_drugs_info.difference(old_drugs_info)
    #print("Taly: new drug info:", len(new_drugs_info), new_drugs_info)

    return new_drugs_info   

################################################################################################
# Queries
################################################################################################
def query_disease_info(session, disease_id):
    """Query disease information."""
    #print(f"\n[Query] Disease info for {disease_id}")
    rows = session.execute("SELECT * FROM disease_info WHERE disease_id = %s", [disease_id])
    output_text = ""
    for row in rows:
        """
        print(f"Disease Name: {row.disease_name}")
        print(f"Drugs: {row.drug_names}")
        print(f"Genes: {row.gene_names}")
        print(f"Locations: {row.location_names}")
        """
        output_text += f"Disease Name: {row.disease_name}\n"
        output_text += f"Drugs: {row.drug_names}\n"
        output_text += f"Genes: {row.gene_names}\n"
        output_text += f"Locations: {row.location_names}\n"

    return output_text

def query_all_disease_info(session):
    """Query all disease information."""
    #print(f"\n[Query] Disease id and name")
    rows = session.execute("SELECT * FROM disease_info")
    output_text = ""
    for row in rows:
        """
        print(f"{row.disease_id}, Disease Name: {row.disease_name}, Drugs: {row.drug_names}")
        """
        output_text += f"{row.disease_id}, Disease Name: {row.disease_name}, Drugs: {row.drug_names}\n"
    return rows

def query_all_new_compounds_info(session):
    #print(f"\n[Query] New Compounds id and name")
    rows = session.execute("SELECT * FROM compound_info")
    output_text = ""
    for row in rows:
        """
        print(f"{row.compound_id}, Compound Name: {row.compound_name}")
        """
        output_text += f"{row.compound_id}, Compound Name: {row.compound_name}\n"

    return output_text

################################################################################################
# Connection with GUI
################################################################################################
def get_result_query1(disease_id):
    #print("run_query1 is called")
    if not is_cassandra_running():
        start_cassandra()
    session = connect_to_cassandra()

    create_keyspace(session)
    create_disease_table(session)

    (disease_names, drugs_names, gene_names, location_names) = load_nodes_information(NODE_DATA_FILE)
    disease_relations = load_disease_relations(EDGE_DATA_FILE)

    insert_disease_info(session, disease_names, drugs_names, gene_names, location_names, disease_relations)

    # Example query for a specific disease
    output_text = query_disease_info(session, disease_id)
    #query_disease_info(session, "Disease::DOID:0050742")

    #query_all_disease_info(session)

    return output_text

def get_result_query2():
    #print("run_query2 is called")
    
    if not is_cassandra_running():
        start_cassandra()
    session = connect_to_cassandra()

    create_keyspace(session)
    create_compound_table(session)
    
    (disease_names, drugs_names, gene_names, location_names) = load_nodes_information(NODE_DATA_FILE)
    compound_gene_anatomy_relations = load_compound_gene_anatomy_relations(EDGE_DATA_FILE)
    anatomy_disease_compound_relations = load_anatomy_desease_compound_relations(EDGE_DATA_FILE)
    new_drugs_info = load_new_drugs_info(compound_gene_anatomy_relations, anatomy_disease_compound_relations)

    insert_compounds_info(session, drugs_names, new_drugs_info)

    # Example query 
    output_text = query_all_new_compounds_info(session)

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
            "   iven a disease id, what is its name,\n"
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
        #print("Result of Query 1")
        user_text = self.entry.get()  # Get the text entered by the user
        
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
        #print("Result of Query 2")
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