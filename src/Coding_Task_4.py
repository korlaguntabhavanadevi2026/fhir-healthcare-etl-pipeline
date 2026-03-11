import json
import requests
from pprint import pprint
from pathlib import Path
from src.registration import data_dir


PRIMARY_EHR_BASE_URL = "http://137.184.71.65:8080/fhir"
BASE_DIR = Path(__file__).resolve().parent
PROCEDURE_OUTPUT_PATH = BASE_DIR / "data" / "coding_task4_output.json"
INPUT_FILE = BASE_DIR / "data" / "coding_task1_output.json"

def get_ehr_headers():
    token_file = Path(data_dir / "access_token.json")
    if not token_file.exists():
        print("[ERROR] access_token.json file not found.")
        return None
    try:
        with open(token_file, 'r') as f:
            token = json.load(f).get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/fhir+json"
            }
    except Exception as e:
        print(f"[ERROR] Error loading token: {e}")
        return None

def load_patient_data():
    if not INPUT_FILE.exists():
        print("[ERROR] Task 1 output file not found.")
        return None
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def create_procedure_resource(patient_id):
    return {
        "resourceType": "Procedure",
        "status": "completed",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "73761001",
                    "display": "Electroencephalography"
                }
            ],
            "text": "EEG (Electroencephalography)"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "performedDateTime": "2024-04-15T09:00:00Z",
        "performer": [
            {
                "actor": {
                    "reference": "Practitioner/4",
                    "display": "Dr. A. Neurologist"
                }
            }
        ],
        "note": [
            {
                "text": "EEG performed due to patient's epilepsy history. Awaiting analysis from neurologist."
            }
        ]
    }

def post_procedure(procedure_data):
    headers = get_ehr_headers()
    if not headers:
        print("[ERROR] Missing authorization headers.")
        return

    response = requests.post(f"{PRIMARY_EHR_BASE_URL}/Procedure", headers=headers, json=procedure_data)
    if response.status_code in [200, 201]:
        response_data = response.json()
        procedure_id = response_data.get("id", "N/A")
        print(f"[SUCCESS] Procedure posted with ID: {procedure_id}")
        PROCEDURE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PROCEDURE_OUTPUT_PATH, 'w') as f:
            json.dump(response_data, f, indent=2)

        print("[SUCCESS] Procedure created and saved to coding_task4_output.json")
    else:
        print(f"[ERROR] Failed to post Procedure. Status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == '__main__':
    patient_data = load_patient_data()
    if not patient_data:
        exit(1)

    patient_id = patient_data.get("primary_patient_id")
    if not patient_id:
        print("[ERROR] No primary patient ID found.")
    else:
        print(f"Using Patient ID: {patient_id}")
        procedure = create_procedure_resource(patient_id)
        post_procedure(procedure)
