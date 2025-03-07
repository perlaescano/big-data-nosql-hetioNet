# Environment Setup Guide (Based on Macos)

## Prerequisites
    – Install Java 8 or Java 11
## Download Cassandra
    – https://cassandra.apache.org/_/download.html
## Configuration
    – In conf/cassandra.yaml
## Getting started
    – http://cassandra.apache.org/doc/latest/getting_started/index.html

## Python Driver (DataStax Cassandra Driver)
    – https://docs.datastax.com/en/developer/python-driver/

## Detail steps for setup
1. Download, extract and move Cassandra
Download the latest stable release: apache-cassandra-4.1.8-bin.tar
Extract: tar -xvzf apache-cassandra-4.1.8-bin.tar
Move the extracted folder to a permanent location: ex sudo mv apache-cassandra-4.1.8 /opt/cassandra
Nevigate to the Cassandra directory

2. Setup environment variables
Open your shell configuration file: sudo nano ~/.zshrc
Add the following lines at the bottom:
export CASSANDRA_HOME=/opt/cassandra
export PATH=$CASSANDRA_HOME/bin:$PATH
Save and exit
Reload the terminal configuration: source ~/.zshrc

3. Start Cassandra
study_cassandra % cassandra -f (foreground)
study_cassandra % cassandra (background)
nodetool status (check if Cassandra is running): If you see UN(Up/Normal), Cassandra is running successfully

study_cassandra % nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address    Load       Tokens  Owns (effective)  Host ID                               Rack 
UN  127.0.0.1  75.75 KiB  16      100.0%            c0ed76ed-ae82-46da-a767-e14d6269fa60  rack1

4. Connect to Cassandra by CQL shell (Cassandra Query Language shell) to interact with the database
study_cassandra % cqlsh
Connected to Test Cluster at 127.0.0.1:9042
[cqlsh 6.1.0 | Cassandra 4.1.8 | CQL spec 3.4.6 | Native protocol v5]
Use HELP for help.
cqlsh> exit

5. Stop Cassandra
study_cassandra % pkill -f cassandra 
or
study_cassandra % nodetool drain && pkill -f cassandra

6. Install the Cassandra Python Driver
study_cassandra % pip install cassandra-driver
or
study_cassandra % conda install -c conda-forge cassandra-driver

7. Verify the Python Driver installation
study_cassandra % python                     
Python 3.9.21 | packaged by conda-forge | (main, Dec  5 2024, 13:47:18) 
[Clang 18.1.8 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import cassandra
>>> print(cassandra.__version__)
3.29.2
>>> 

# Run python script
