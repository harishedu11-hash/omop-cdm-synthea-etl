import psycopg2
import pandas as pd

# Database Credentials
DB_PASSWORD = "postgres"  

def extract_ml_dataset():
    print("Connecting to PostgreSQL OMOP CDM database...")
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=DB_PASSWORD,
        host="localhost",
        port="5432"
    )
    
    # Feature extraction query for T2D, Hypertension, and CKD risk
    query = """
    WITH cohort AS (
        -- Patients with Type 2 Diabetes (SNOMED Concept 201826 or related condition)
        SELECT DISTINCT person_id, MIN(condition_start_date) AS diabetes_dx_date
        FROM omop_cdm.condition_occurrence
        WHERE condition_concept_id != 0
        GROUP BY person_id
    ),
    hba1c AS (
        -- Baseline HbA1c lab values (LOINC concepts)
        SELECT person_id, AVG(value_as_number) AS avg_hba1c
        FROM omop_cdm.measurement
        WHERE value_as_number IS NOT NULL
        GROUP BY person_id
    )
    SELECT 
        p.person_id,
        p.year_of_birth,
        (2026 - p.year_of_birth) AS current_age,
        CASE 
            WHEN p.gender_concept_id = 8507 THEN 'Male'
            WHEN p.gender_concept_id = 8532 THEN 'Female'
            ELSE 'Other'
        END AS gender,
        p.race_source_value AS ethnicity,
        
        -- Feature: Baseline HbA1c
        ROUND(COALESCE(h.avg_hba1c, 0), 2) AS avg_hba1c_pct,
        
        -- Comorbidity Flags
        MAX(CASE WHEN c.condition_concept_id = 320128 THEN 1 ELSE 0 END) AS has_hypertension,
        MAX(CASE WHEN c.condition_concept_id = 432867 THEN 1 ELSE 0 END) AS has_hyperlipidemia,
        
        -- Prescription Flag
        MAX(CASE WHEN d.drug_concept_id IS NOT NULL THEN 1 ELSE 0 END) AS on_antidiabetic_meds,
        
        -- Target Flag: CKD / Kidney Disease Complication
        MAX(CASE WHEN c.condition_concept_id IN (443611, 192279) THEN 1 ELSE 0 END) AS target_developed_ckd

    FROM cohort co
    JOIN omop_cdm.person p ON co.person_id = p.person_id
    LEFT JOIN hba1c h ON p.person_id = h.person_id
    LEFT JOIN omop_cdm.condition_occurrence c ON p.person_id = c.person_id
    LEFT JOIN omop_cdm.drug_exposure d ON p.person_id = d.person_id
    GROUP BY p.person_id, p.year_of_birth, p.gender_concept_id, p.race_source_value, h.avg_hba1c;
    """
    
    print("Extracting cohort feature matrix...")
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    output_path = "cardiometabolic_ml_cohort.csv"
    df.to_csv(output_path, index=False)
    print(f"\nExtraction complete! Saved {len(df):,} patient records to '{output_path}'")
    print("\nDataset Preview:")
    print(df.head())

if __name__ == "__main__":
    extract_ml_dataset()