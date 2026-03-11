import json
import requests
from pathlib import Path


from pprint import pprint
from src.registration import data_dir

# --- CONFIGURATION ---
OPENEMR_BASE_URL       = "https://in-info-web20.luddy.indianapolis.iu.edu/apis/default/fhir"
PRIMARY_EHR_BASE_URL   = "http://137.184.71.65:8080/fhir"
BASE_HERMES_URL        = 'http://159.65.173.51:8080/v1/snomed'
US_CORE_CONDITION_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"


def get_access_token():
    token_file = Path(data_dir) / "access_token.json"
    if not token_file.exists():
        raise FileNotFoundError("access_token.json not found")
    return json.loads(token_file.read_text())["access_token"]


def get_headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/fhir+json"
    }


def load_task1_output():
    file_path = Path(data_dir) / "coding_task1_output.json"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")
    return json.loads(file_path.read_text())


def constraint_child(code):
    # SNOMED ECL: immediate child operator '<!'
    return f"<! {code}"


def fetch_child_concept(search_string):
    url = f"{BASE_HERMES_URL}/search"
    resp = requests.get(url, params={"constraint": search_string})
    resp.raise_for_status()
    items = resp.json()
    if not items:
        raise ValueError("No child concepts returned")
    first = items[0]
    return {"conceptId": first["conceptId"], "preferredTerm": first["preferredTerm"]}


def create_child_condition(patient_id, concept):
    condition_res = {
        "resourceType": "Condition",
        "meta": {"profile": [US_CORE_CONDITION_PROFILE]},
        "subject": {"reference": f"Patient/{patient_id}"},
        "code": {"coding": [{
            "system": "http://snomed.info/sct",
            "code": concept["conceptId"],
            "display": concept["preferredTerm"]
        }], "text": concept["preferredTerm"]},
        "clinicalStatus": {"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active"
        }]},
        "verificationStatus": {"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "confirmed"
        }]}
    }
    resp = requests.post(
        f"{PRIMARY_EHR_BASE_URL}/Condition", headers=get_headers(), json=condition_res
    )
    resp.raise_for_status()
    return resp.json()["id"]


def validate_and_show(condition_id):
    url = f"{PRIMARY_EHR_BASE_URL}/Condition/{condition_id}"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    cond = resp.json()
    print("\n Validation – meta.profile:")
    pprint(cond.get("meta", {}).get("profile"))


def save_output(bundle):
    out_file = Path(data_dir) / "coding_task2_output.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(bundle, indent=2))
    print(f"Output saved to {out_file}")


if __name__ == "__main__":
    # 1. Load Task 1 data
    data = load_task1_output()
    patient_id = data.get("primary_patient_id")
    original_code = data.get("ConditionCode")
    print(f"Original Condition code: {original_code}")

    # 2. Find a child concept:
    ecl = constraint_child(original_code)
    child = fetch_child_concept(ecl)
    print(f"Child concept → {child['conceptId']} ('{child['preferredTerm']}')")

    # 3. Create Condition on Primary EHR:
    new_cond_id = create_child_condition(patient_id, child)
    print(f" Created Condition/{new_cond_id} on Primary EHR.")

    # 4. Demonstrate validation:
    validate_and_show(new_cond_id)

    # 5. (Optional) fetch and save all conditions for this patient:
    all_conds = requests.get(
        f"{PRIMARY_EHR_BASE_URL}/Condition", headers=get_headers(), params={"patient": patient_id}
    ).json()
    save_output(all_conds)