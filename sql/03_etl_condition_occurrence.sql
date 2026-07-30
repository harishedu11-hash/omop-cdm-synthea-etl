INSERT INTO omop_cdm.condition_occurrence (
    condition_occurrence_id,
    person_id,
    condition_concept_id,
    condition_start_date,
    condition_end_date,
    condition_type_concept_id,
    condition_source_value,
    condition_source_concept_id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY c."PATIENT", c."START") AS condition_occurrence_id,
    p.person_id,
    COALESCE(voc.concept_id, 0) AS condition_concept_id, -- Falls back to 0 if unmapped
    c."START"::DATE AS condition_start_date,
    c."STOP"::DATE AS condition_end_date,
    32817 AS condition_type_concept_id, -- "EHR header record"
    c."CODE"::VARCHAR AS condition_source_value,
    COALESCE(voc.concept_id, 0) AS condition_source_concept_id
FROM raw_synthea.conditions c
JOIN omop_cdm.person p 
  ON c."PATIENT" = p.person_source_value
LEFT JOIN omop_cdm.concept voc 
  ON c."CODE"::VARCHAR = voc.concept_code 
 AND voc.vocabulary_id = 'SNOMED' 
 AND voc.standard_concept = 'S';