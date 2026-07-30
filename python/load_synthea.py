import pandas as pd
from sqlalchemy import create_engine

# Update with your actual PostgreSQL password
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

# Correct path syntax (single pair of quotes, no extra quotes inside):
patients_path = "C:/Users/Harish Mohankumar/Downloads/synthea_sample_data_csv_apr2020/csv/patients.csv"
encounters_path = "C:/Users/Harish Mohankumar/Downloads/synthea_sample_data_csv_apr2020/csv/encounters.csv"
conditions_path = "C:/Users/Harish Mohankumar/Downloads/synthea_sample_data_csv_apr2020/csv/conditions.csv"

# Load raw Synthea CSVs into PostgreSQL staging tables
patients = pd.read_csv(patients_path)
patients.to_sql('patients', engine, schema='raw_synthea', if_exists='replace', index=False)

encounters = pd.read_csv(encounters_path)
encounters.to_sql('encounters', engine, schema='raw_synthea', if_exists='replace', index=False)

conditions = pd.read_csv(conditions_path)
conditions.to_sql('conditions', engine, schema='raw_synthea', if_exists='replace', index=False)

print("Raw CSVs loaded into PostgreSQL staging successfully!")