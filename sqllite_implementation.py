import sqlite3
import pandas as pd

# Function to create a SQLite database from CSV files
def create_db_from_csv(db_name, csv_files, table_names):
    conn = sqlite3.connect(db_name)
    for csv_file, table_name in zip(csv_files, table_names):
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

# Function to read back data from the SQLite database
def read_data_from_db(db_name, table_name):
    conn = sqlite3.connect(db_name)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# CSV file paths and table names
csv_files = ['./dataset_files/dim_match_summary.csv', './dataset_files/dim_players.csv', './dataset_files/fact_bating_summary.csv', './dataset_files/fact_bowling_summary.csv']
table_names = ['dim_match_summary', 'dim_players', 'fact_bating_summary', 'fact_bowling_summary']

# Function to export tables from SQLite database to CSV files
def export_db_to_csv(db_name, table_names, output_csv_files):
    conn = sqlite3.connect(db_name)
    for table_name, output_csv in zip(table_names, output_csv_files):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        df.to_csv(output_csv, index=False)
    conn.close()

# Database name
db_name = 'my__ipl_database.db'

# Create database from CSV files
create_db_from_csv(db_name, csv_files, table_names)

# Example of reading back data from one of the tables
df_table1 = read_data_from_db(db_name, 'dim_match_summary')
print(df_table1)
