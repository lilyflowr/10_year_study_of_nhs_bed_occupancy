CREATE TABLE raw_clinical_encounters (
    encounter_id VARCHAR(20) PRIMARY KEY,
	patient_id VARCHAR(20) NOT NULL,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	date_of_birth DATE NOT NULL,
	phone_number VARCHAR (30),
	admission_date DATE NOT NULL,
	discharge_date DATE NOT NULL,
	primary_diagnosis VARCHAR(100) NOT NULL,
	length_of_stay_days INT NOT NULL,
	readmission_30_days VARCHAR(5) NOT NULL,
	encounter_cost_usd NUMERIC(10, 2) NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW vw_clinical_full_access AS
SELECT *
FROM raw_clinical_encounters;

CREATE VIEW vw_analyst_deidentified AS
SELECT
   encounter_id,
   patient_id,
   admission_date,
   discharge_date,
   primary_diagnosis,
   length_of_stay_days,
   readmission_30_days,
   encounter_cost_usd
 FROM raw_clinical_encounters;

SELECT *
FROM raw_clinical_encounters;

SELECT COUNT(*) 
FROM raw_clinical_encounters;