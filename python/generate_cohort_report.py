import pandas as pd
from sqlalchemy import create_engine

# Database Connection via SQLAlchemy Engine
DB_PASSWORD = "postgres"  # Replace with your PostgreSQL password
engine = create_engine(f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/postgres")

def generate_attrition_report():
    query = """
    SELECT 
        cd.cohort_definition_id,
        cd.cohort_definition_name,
        COUNT(c.subject_id) AS total_subjects,
        MIN(c.cohort_start_date) AS earliest_index_date,
        MAX(c.cohort_start_date) AS latest_index_date
    FROM omop_cdm.cohort_definition cd
    LEFT JOIN omop_cdm.cohort c ON cd.cohort_definition_id = c.cohort_definition_id
    GROUP BY cd.cohort_definition_id, cd.cohort_definition_name;
    """
    
    print("Generating OHDSI Cohort Summary...")
    df = pd.read_sql_query(query, engine)
    
    print("\n--- OHDSI Phenotype Cohort Summary ---")
    print(df.to_string(index=False))
    
    output_path = "ohdsi_cohort_summary.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSummary successfully saved to '{output_path}'")

if __name__ == "__main__":
    generate_attrition_report()