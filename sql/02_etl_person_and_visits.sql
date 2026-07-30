INSERT INTO omop_cdm.person (
    person_id,
    gender_concept_id,
    year_of_birth,
    month_of_birth,
    day_of_birth,
    birth_datetime,
    race_concept_id,
    ethnicity_concept_id,
    person_source_value,
    gender_source_value,
    race_source_value
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY "Id") AS person_id,
    CASE 
        WHEN UPPER("GENDER") = 'M' THEN 8507
        WHEN UPPER("GENDER") = 'F' THEN 8532
        ELSE 0 
    END AS gender_concept_id,
    EXTRACT(YEAR FROM "BIRTHDATE"::DATE) AS year_of_birth,
    EXTRACT(MONTH FROM "BIRTHDATE"::DATE) AS month_of_birth,
    EXTRACT(DAY FROM "BIRTHDATE"::DATE) AS day_of_birth,
    "BIRTHDATE"::TIMESTAMP AS birth_datetime,
    CASE 
        WHEN LOWER("RACE") = 'white' THEN 8527
        WHEN LOWER("RACE") = 'black' THEN 8516
        WHEN LOWER("RACE") = 'asian' THEN 8515
        ELSE 0
    END AS race_concept_id,
    0 AS ethnicity_concept_id,
    "Id" AS person_source_value,
    "GENDER" AS gender_source_value,
    "RACE" AS race_source_value
FROM raw_synthea.patients;


INSERT INTO omop_cdm.observation_period (
    observation_period_id,
    person_id,
    observation_period_start_date,
    observation_period_end_date,
    period_type_concept_id
)
SELECT 
    p.person_id AS observation_period_id,
    p.person_id,
    MIN(e."START"::DATE) AS observation_period_start_date,
    MAX(e."STOP"::DATE) AS observation_period_end_date,
    32817 AS period_type_concept_id -- OMOP concept for "EHR Administration record"
FROM raw_synthea.encounters e
JOIN omop_cdm.person p ON e."PATIENT" = p.person_source_value
GROUP BY p.person_id;


INSERT INTO omop_cdm.visit_occurrence (
    visit_occurrence_id,
    person_id,
    visit_concept_id,
    visit_start_date,
    visit_end_date,
    visit_type_concept_id,
    visit_source_value
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY e."Id") AS visit_occurrence_id,
    p.person_id,
    CASE 
        WHEN LOWER(e."ENCOUNTERCLASS") = 'inpatient' THEN 9201
        WHEN LOWER(e."ENCOUNTERCLASS") = 'outpatient' THEN 9202
        WHEN LOWER(e."ENCOUNTERCLASS") = 'emergency' THEN 9203
        WHEN LOWER(e."ENCOUNTERCLASS") = 'wellness' THEN 9202
        ELSE 0
    END AS visit_concept_id,
    e."START"::DATE AS visit_start_date,
    e."STOP"::DATE AS visit_end_date,
    32817 AS visit_type_concept_id, -- "EHR encounter record"
    e."ENCOUNTERCLASS" AS visit_source_value
FROM raw_synthea.encounters e
JOIN omop_cdm.person p ON e."PATIENT" = p.person_source_value;