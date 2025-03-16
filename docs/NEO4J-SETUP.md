# Neo4j Setup

## Install Neo4j
### **Download and Install Neo4j**
```bash
brew install neo4j
```

### **Start Neo4j**
```bash
neo4j start
```

### **Set Up Neo4j User and Password (via Terminal)**
1. Open a terminal and **start the Neo4j shell** using:
   ```bash
   cypher-shell -u neo4j -p neo4j
   ```
   - `-u` specifies the **username** (`neo4j` by default)
   - `-p` specifies the **password** (default is `neo4j`)
   
2. When prompted, change the default password:
   ```cypher
   CALL dbms.security.changeUserPassword('<your-password>');
   ```
   Replace `<your-password>` with a secure password of your choice.

3. Exit the shell:
   ```bash
   :exit
   ```

### **Create the `.env` file** (in your project root)
Create a new `.env` file and add the following lines:
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
```

### **Python Scripts Automatically Load `.env`**
You do **not** need to manually load environment variables. The project uses `python-dotenv`, which automatically reads from `.env` when running scripts.


## Install Required Python Packages
```bash
pip install -r requirements.txt
```

## Run Neo4j Scripts
### **Test Neo4j Connection**
```bash
python scripts_neo4j/db_connection.py
```

### **Load Data into Neo4j**
```bash
python scripts_neo4j/load_data.py
```

### **Run Queries via Terminal**
```bash
python scripts_neo4j/queries.py 1 Disease::DOID:1686
```
```bash
python scripts_neo4j/queries.py 2
```

### **Run Neo4j GUI Interface**
```bash
python scripts_neo4j/gui.py
```

