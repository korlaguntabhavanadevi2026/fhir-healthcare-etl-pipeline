import json
import requests
from pathlib import Path
from datetime import datetime

# Base directory for portability:
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# File paths
TOKEN_FILE = DATA_DIR / "access_token.json"
INPUT_FILE = DATA_DIR / "coding_task1_output.json"
OUTPUT_FILE = DATA_DIR / "coding_task3_output.json"
BASE_OBSERVATION_URL = "http://137.184.71.65:8080/fhir/Observation"

# Load access token from file:
def get_access_token_from_file():
    if not TOKEN_FILE.exists():
        print("[ERROR] Token file missing.")
        return None
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f).get("access_token")

# Build headers
def get_headers():
    token = get_access_token_from_file()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# Load patient resource ID from coding task 1 output:
def get_patient_resource_id():
    if not INPUT_FILE.exists():
        print("[ERROR] Patient output file not found.")
        return None
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        return data.get("primary_patient_id")

# Create observation resource:
def create_bp_observation(patient_id):
    return {
        "resourceType": "Observation",
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/vitalsigns"]
        },
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "85354-9",
                "display": "Blood pressure panel with all children optional"
            }],
            "text": "Blood pressure systolic & diastolic"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "performer": [{
            "reference": "Practitioner/4"
        }],
        "bodySite": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "368209003",
                "display": "Right arm"
            }]
        },
        "component": [
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure"
                    }]
                },
                "valueQuantity": {
                    "value": 120,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8462-4",
                        "display": "Diastolic blood pressure"
                    }]
                },
                "valueQuantity": {
                    "value": 80,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    }

# Post observation to server and save output:
def post_observation_to_server(observation_data):
    try:
        response = requests.post(BASE_OBSERVATION_URL, headers=get_headers(), json=observation_data, timeout=10)
        if response.status_code in [200, 201]:
            response_json = response.json()
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(response_json, f, indent=2)
            print("[SUCCESS] Observation created and saved to coding_task3_output.json")
        else:
            print(f"[ERROR] Failed to post observation. Status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"[EXCEPTION] Request error: {e}")

# Main logic:
if __name__ == "__main__":
    patient_resource_id = get_patient_resource_id()
    if patient_resource_id:
        observation = create_bp_observation(patient_resource_id)
        post_observation_to_server(observation)
    else:
        print("[ERROR] Could not retrieve patient resource ID.")
