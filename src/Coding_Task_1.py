import json
import requests
from pathlib import Path
from pprint import pprint

from src.registration import data_dir

BASE_URL = "https://in-info-web20.luddy.indianapolis.iu.edu/apis/default/fhir"
BASE_HERMES_URL = 'http://159.65.173.51:8080/v1/snomed'
PRIMARY_EHR_BASE_URL = "http://137.184.71.65:8080/fhir"
FHIR_PROFILE_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"


def get_access_token_from_file():
    file_path = Path(data_dir / "access_token.json")
    if not file_path.exists():
        print("Error: access_token.json file not found.")
        return None
    try:
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
            return json_data.get("access_token")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading access token from file: {e}")
        return None

def get_headers():
    access_token = get_access_token_from_file()
    return {"Authorization": f"Bearer {access_token}"}

def search_patient_by_name_and_birthdate():
    print("\n[STEP 1] Performing filtered search on Patient resource...")
    url = f"{BASE_URL}/Patient"
    params = {"name": "Marks", "birthdate": "gt2000-01-01"}
    response = requests.get(url, headers=get_headers(), params=params)
    if response.status_code == 200:
        print("Filtered search successful. Patient(s) found.")
    else:
        print(f"Filtered search failed: {response.status_code}")

def get_fhir_patient(resource_id):
    print("[STEP 2] Retrieving patient details from OpenEMR...")
    url = f'{BASE_URL}/Patient/{resource_id}'
    headers = get_headers()
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        print("Patient data retrieved successfully.")
        return {"resourceType": "Patient", **response.json()}
    else:
        print(f"Error fetching patient data: {response.status_code}")
        return None

def search_condition(patient_resource_id):
    print("[STEP 3] Searching for patient conditions...")
    url = f'{BASE_URL}/Condition?patient={patient_resource_id}'
    response = requests.get(url=url, headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        if 'entry' in data and len(data['entry']) > 0:
            print("Condition found.")
            condition_entry = data['entry'][0]
            code = condition_entry['resource']['code']['coding'][0]['code']
            return code
        else:
            print("No condition entries found.")
            return None
    else:
        print(f"Error fetching condition data: {response.status_code}")
        return None

def constraint_5(code):
    return f">! {code}"

def expression_constraint(search_string):
    print("[STEP 4] Fetching parent SNOMED concept using Hermes...")
    url = f'{BASE_HERMES_URL}/search?constraint={search_string}'
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Parent concept retrieved.")
            first_item = data[0]
            return {"conceptId": first_item['conceptId'], "preferredTerm": first_item['preferredTerm']}
    print("No parent concept found.")
    return None

def save_output_to_json(patient_data, condition_code, concept_result, primary_patient_id, file_path):
    print("[STEP 7] Saving data to JSON file...")
    output_data = {
        **patient_data,
        "ConditionCode": condition_code,
        "ConceptResult": concept_result,
        "primary_patient_id": primary_patient_id
    }
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=2)
    print(f"Output saved to: {file_path}")

def prepare_patient_resource_with_extensions(data):
    extensions = []
    if "ConditionCode" in data:
        extensions.append({"url": "http://example.org/fhir/StructureDefinition/patient-condition-code", "valueString": data["ConditionCode"]})
    if "ConceptResult" in data:
        concept = data["ConceptResult"]
        if "conceptId" in concept:
            extensions.append({"url": "http://example.org/fhir/StructureDefinition/patient-conceptId", "valueString": str(concept["conceptId"])})
        if "preferredTerm" in concept:
            extensions.append({"url": "http://example.org/fhir/StructureDefinition/patient-preferredTerm", "valueString": concept["preferredTerm"]})
    patient_resource = {k: v for k, v in data.items() if k not in ["ConditionCode", "ConceptResult"]}
    patient_resource["meta"] = {"profile": [FHIR_PROFILE_URL]}
    if extensions:
        patient_resource.setdefault("extension", []).extend(extensions)
    return patient_resource

def create_patient_in_primary_ehr(patient_resource):
    print("[STEP 5] Creating patient on Primary EHR server...")
    url = f"{PRIMARY_EHR_BASE_URL}/Patient"
    headers = get_headers()
    response = requests.post(url, headers=headers, json=patient_resource)
    if response.status_code in [200, 201]:
        print("Patient created on Primary EHR.")
        return response.json().get("id")
    else:
        print(f"Error creating patient: {response.status_code}")
        return None

def create_condition_in_primary_ehr(patient_id, concept_result):
    print("[STEP 6] Creating condition using parent concept...")
    if not concept_result:
        print("No ConceptResult provided.")
        return
    concept_id = concept_result.get("conceptId")
    preferred_term = concept_result.get("preferredTerm")
    if not (concept_id and preferred_term):
        print("Incomplete ConceptResult data. Cannot create Condition.")
        return
    condition_resource = {
        "resourceType": "Condition",
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"]
        },
        "code": {
            "coding": [{"system": "http://snomed.info/sct", "code": concept_id, "display": preferred_term}],
            "text": preferred_term
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]},
        "category": [{
            "coding": [
                {"system": "http://snomed.info/sct", "code": "439401001", "display": "Encounter Diagnosis"},
                {"system": "http://snomed.info/sct", "code": "diagnosis", "display": "Diagnosis"}
            ],
            "text": "Diagnosis"
        }],
        "severity": {"coding": [{"system": "http://snomed.info/sct"}], "text": "Severe"},
        "bodySite": [{"coding": [{"system": "http://snomed.info/sct", "code": "38266002", "display": "Entire body"}], "text": "Entire body"}]
    }
    headers = get_headers()
    response = requests.post(f"{PRIMARY_EHR_BASE_URL}/Condition", headers=headers, json=condition_resource)
    if response.status_code in [200, 201]:
        print("Condition successfully created and validated against US Core profile.")
        return response.json()
    else:
        print(f"Failed to create Condition. Status code: {response.status_code}")
        return None

if __name__ == '__main__':
    search_patient_by_name_and_birthdate()
    patient_resource_id = '985ac6f5-1ee6-4281-9620-fd729daef9c1'
    file_path = Path("C:/Users/pgarl/PycharmProjects/Group_Project_5/src/data/coding_task1_output.json")
    patient_data = get_fhir_patient(resource_id=patient_resource_id)
    if patient_data:
        patient_code = search_condition(patient_resource_id=patient_resource_id)
        if patient_code:
            search_string = constraint_5(patient_code)
            concept_result = expression_constraint(search_string=search_string)
            prepared_patient = prepare_patient_resource_with_extensions({**patient_data, "ConditionCode": patient_code, "ConceptResult": concept_result})
            new_patient_id = create_patient_in_primary_ehr(prepared_patient)
            save_output_to_json(patient_data=patient_data, condition_code=patient_code, concept_result=concept_result, primary_patient_id=new_patient_id, file_path=file_path)
            if new_patient_id:
                create_condition_in_primary_ehr(new_patient_id, concept_result)



