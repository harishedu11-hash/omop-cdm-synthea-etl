import os
import pandas as pd
from sqlalchemy import create_engine

# Database connection settings
DB_PASSWORD = "postgres"  
SYNTHEA_DIR = r"C:\Users\Harish Mohankumar\Downloads\synthea_sample_data_csv_apr2020\csv"
engine = create_engine(f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/postgres")

files_to_load = [
    ("medications.csv", "medications"),
    ("observations.csv", "observations")
]

print("Loading remaining Synthea raw files into PostgreSQL...")

for file_name, table_name in files_to_load:
    file_path = os.path.join(SYNTHEA_DIR, file_name)
    if os.path.exists(file_path):
        print(f"Reading {file_name}...")
        df = pd.read_csv(file_path, dtype=str)
        
        # Load into raw_synthea schema
        df.to_sql(
            name=table_name,
            con=engine,
            schema="raw_synthea",
            if_exists="replace",
            index=False
        )
        print(f"Successfully loaded {len(df):,} rows into raw_synthea.{table_name}!")
    else:
        print(f"File not found: {file_path}")

print("Staging complete!")