# Project Group 2

### [Click here to visit our website](https://pages.github.iu.edu/sashire/Group_Project_2/)

## Project Description

This project implements an end-to-end ETL (Extract, Transform, Load) pipeline for healthcare data integration using FHIR (Fast Healthcare Interoperability Resources) APIs. The goal is to facilitate the secure exchange and transformation of patient health information between FHIR-compatible systems.

The pipeline includes the following stages:

- **Extraction**: Patient data is retrieved securely from a source FHIR API (OpenEMR) using authenticated API requests.
- **Transformation**: Retrieved data is mapped and formatted using standardized coding systems (e.g., SNOMED CT to ICD-10). Additional resources such as blood pressure observations and procedures are created.
- **Loading**: Transformed resources are sent to a secondary FHIR API to simulate data integration across systems.
- **Interoperability**: Data is converted into HL7 v2 message format to demonstrate compatibility with legacy health information systems.

Key components of the project include:

- Patient demographic retrieval and formatting
- SNOMED CT child term lookup via Hermes API
- ICD-10 mapping from SNOMED using the Hermes mapping service
- Observation and procedure resource creation
- HL7 v2 message generation using `hl7apy`

## Authentication and Authorization

The pipeline uses OAuth 2.0 authorization with access tokens and refresh tokens to interact with the FHIR APIs securely.

1. **Authorization Code Flow**:
   - A user visits the FHIR authorization endpoint and grants access.
   - The resulting authorization code is stored in a file (`url_from_browser.txt`).

2. **Access Token Retrieval**:
   - A script exchanges the authorization code for an access token and refresh token using the token endpoint.
   - The token is saved in `access_token.json` and used in the `Authorization` header of all API requests.

3. **Refresh Token Handling**:
   - If the access token expires, the refresh token can be used to obtain a new token using the refresh flow.
   - This ensures uninterrupted access to secured APIs during long-running scripts.

## Instructions on running the tasks
### Coding Task 1: 
- Searches for a patient on the **OpenEMR FHIR server** using filters like name, birthdate, etc. (done prior to this task).
- Extracts the SNOMED condition code from that patient's Condition resource.
- Uses the Hermes Terminology Server with the constraint `< code` to find a **child SNOMED concept**.
- Creates a new **Patient** and a new **Condition** using that child SNOMED concept on the **Primary Care FHIR server**.
- Saves the new patient ID and condition code to `coding_task1_output.json` for use in later tasks.

### Coding Task 2:
- Uses `primary_patient_id` from Task 1’s output.
- Sends a GET request to fetch **all Condition resources** for that patient from the **Primary Care FHIR server**.
- Output: `coding_task2_output.json`.

### Coding Task 3:
- Uses the `primary_patient_id` from Task 1.
- Constructs an **Observation** resource coded with **LOINC** for **systolic and diastolic blood pressure**.
- Posts the Observation to the **Primary Care FHIR server**.
- Output: `coding_task3_output.json`.

### Coding Task 4
- Uses the `primary_patient_id` from Task 1.
- Creates a **Procedure** resource for **Electroencephalography (EEG)** using SNOMED CT.
- Adds details such as performing practitioner and notes.
- Posts to the **Primary Care FHIR server**.
- Output: `coding_task4_output.json`.

### Coding Task 5
- Loads patient and condition data from `coding_task1_output.json` and `coding_task2_output.json`.
- For each condition, uses Hermes to map the SNOMED code to an **ICD-10 code**.
- Constructs an **HL7 v2 ADT^A01 message** using `hl7apy`, including `MSH`, `PID`, `PV1`, and `DG1` segments.
- Saves the message in HL7 pipe-delimited format.
- Output: `task_5_hl7.txt`.

### Visualization 
- Fetches patient resources from the **OpenEMR FHIR server**.
- Analyzes the **gender distribution** among patients.
- Plots the results using `matplotlib`.
- Saves the bar chart as `assets/gender_distribution.png`.

## Additional Notes & Dependencies

- Make sure you're using **Python 3.8 or above**.
- Before running any script, install the required packages mentioned in the instructions above:
  ```bash
  pip install requests hl7apy matplotlib
  
## Thank You

Best,

Group 2



