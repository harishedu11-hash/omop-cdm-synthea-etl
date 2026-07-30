-- 1. DRUG_EXPOSURE Table
CREATE TABLE IF NOT EXISTS omop_cdm.drug_exposure (
    drug_exposure_id BIGINT NOT NULL,
    person_id BIGINT NOT NULL,
    drug_concept_id INT NOT NULL,
    drug_exposure_start_date DATE NOT NULL,
    drug_exposure_end_date DATE NOT NULL,
    drug_type_concept_id INT NOT NULL,
    stop_reason VARCHAR(20) NULL,
    refills INT NULL,
    quantity NUMERIC NULL,
    days_supply INT NULL,
    sig TEXT NULL,
    route_concept_id INT NULL,
    lot_number VARCHAR(50) NULL,
    provider_id BIGINT NULL,
    visit_occurrence_id BIGINT NULL,
    drug_source_value VARCHAR(50) NULL,
    drug_source_concept_id INT NULL
);

-- 2. MEASUREMENT Table (for Labs like HbA1c, BP, LDL)
CREATE TABLE IF NOT EXISTS omop_cdm.measurement (
    measurement_id BIGINT NOT NULL,
    person_id BIGINT NOT NULL,
    measurement_concept_id INT NOT NULL,
    measurement_date DATE NOT NULL,
    measurement_datetime TIMESTAMP NULL,
    measurement_time VARCHAR(10) NULL,
    measurement_type_concept_id INT NOT NULL,
    operator_concept_id INT NULL,
    value_as_number NUMERIC NULL,
    value_as_concept_id INT NULL,
    unit_concept_id INT NULL,
    range_low NUMERIC NULL,
    range_high NUMERIC NULL,
    provider_id BIGINT NULL,
    visit_occurrence_id BIGINT NULL,
    measurement_source_value VARCHAR(50) NULL,
    measurement_source_concept_id INT NULL,
    unit_source_value VARCHAR(50) NULL,
    value_source_value VARCHAR(50) NULL
);



INSERT INTO omop_cdm.measurement (
    measurement_id,
    person_id,
    measurement_concept_id,
    measurement_date,
    measurement_type_concept_id,
    value_as_number,
    measurement_source_value,
    measurement_source_concept_id,
    unit_source_value
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY o."PATIENT", o."DATE") AS measurement_id,
    p.person_id,
    COALESCE(voc.concept_id, 0) AS measurement_concept_id,
    o."DATE"::DATE AS measurement_date,
    32817 AS measurement_type_concept_id, -- "EHR lab result"
    CASE 
        WHEN o."VALUE" ~ '^[0-9.]+$' THEN o."VALUE"::NUMERIC 
        ELSE NULL 
    END AS value_as_number,
    o."CODE"::VARCHAR AS measurement_source_value,
    COALESCE(voc.concept_id, 0) AS measurement_source_concept_id,
    o."UNITS" AS unit_source_value
FROM raw_synthea.observations o
JOIN omop_cdm.person p ON o."PATIENT" = p.person_source_value
LEFT JOIN omop_cdm.concept voc 
  ON o."CODE"::VARCHAR = voc.concept_code 
 AND voc.vocabulary_id = 'LOINC' 
 AND voc.standard_concept = 'S';