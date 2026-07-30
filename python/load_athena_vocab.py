import os
import pandas as pd
import psycopg2

# Configuration
DB_PASSWORD = "postgres"  # Your PostgreSQL password
VOCAB_DIR = "C:/Users/Harish Mohankumar/Desktop/OMOP_Projects/vocabulary_download_v5_{0bc241ed-f047-4183-a763-9c3bce8b0ce8}_1785266974869"

def load_table(csv_name, table_name, schema="omop_cdm", parse_dates=False):
    file_path = os.path.join(VOCAB_DIR, csv_name)
    
    if not os.path.exists(file_path):
        print(f"Skipping {csv_name}: File not found in {VOCAB_DIR}")
        return

    print(f"Reading {csv_name}...")
    
    # Read tab-delimited file, keep empty strings as empty strings
    df = pd.read_csv(file_path, sep="\t", dtype=str, quoting=3, on_bad_lines="skip", keep_default_na=False)
    
    # Convert dataframe column names to lowercase to match PostgreSQL schema
    df.columns = df.columns.str.lower()

    # Fill empty concept names AND truncate extra long descriptions to max 1000 chars
    if table_name == "concept" and "concept_name" in df.columns:
        df["concept_name"] = df["concept_name"].replace("", "No Name Provided")
        df["concept_name"] = df["concept_name"].str.slice(0, 1000)

    # Convert YYYYMMDD to YYYY-MM-DD for PostgreSQL DATE types
    if parse_dates:
        for date_col in ["valid_start_date", "valid_end_date"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=DB_PASSWORD,
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    
    from io import StringIO
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
    buffer.seek(0)
    
    print(f"Bulk loading into {schema}.{table_name}...")
    try:
        columns = ", ".join(df.columns)
        copy_sql = f"COPY {schema}.{table_name} ({columns}) FROM STDIN WITH (FORMAT text, DELIMITER '\t', NULL '\\N')"
        cursor.copy_expert(sql=copy_sql, file=buffer)
        conn.commit()
        print(f"Successfully loaded {len(df):,} rows into {schema}.{table_name}!\n")
    except Exception as e:
        conn.rollback()
        print(f"Error loading {table_name}: {e}\n")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Starting Athena Vocabulary Load Engine...\n")
    
    load_table("CONCEPT.csv", "concept", parse_dates=True)
    load_table("CONCEPT_RELATIONSHIP.csv", "concept_relationship", parse_dates=True)
    load_table("CONCEPT_ANCESTOR.csv", "concept_ancestor", parse_dates=False)
    
    print("All requested vocabulary tables processed!")