INSERT INTO omop_cdm.drug_exposure (
    drug_exposure_id,
    person_id,
    drug_concept_id,
    drug_exposure_start_date,
    drug_exposure_end_date,
    drug_type_concept_id,
    drug_source_value,
    drug_source_concept_id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY m."PATIENT", m."START") AS drug_exposure_id,
    p.person_id,
    COALESCE(voc.concept_id, 0) AS drug_concept_id,
    m."START"::DATE AS drug_exposure_start_date,
    COALESCE(NULLIF(m."STOP", '')::DATE, m."START"::DATE) AS drug_exposure_end_date,
    32817 AS drug_type_concept_id, -- "EHR prescription status"
    m."CODE"::VARCHAR AS drug_source_value,
    COALESCE(voc.concept_id, 0) AS drug_source_concept_id
FROM raw_synthea.medications m
JOIN omop_cdm.person p ON m."PATIENT" = p.person_source_value
LEFT JOIN omop_cdm.concept voc 
  ON m."CODE"::VARCHAR = voc.concept_code 
 AND voc.vocabulary_id IN ('RxNorm', 'RxNorm Extension');