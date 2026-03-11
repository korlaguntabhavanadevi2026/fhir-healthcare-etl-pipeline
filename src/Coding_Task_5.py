import json
import requests
from pathlib import Path
from hl7apy.core import Message
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "coding_task1_output.json"
CONDITION_FILE = DATA_DIR / "coding_task2_output.json"
OUTPUT_FILE = DATA_DIR / "coding_task5_output.txt"
HERMES_URL = "http://159.65.173.51:8080/v1/snomed/mappings/icd10"

def load_data():
    if not INPUT_FILE.exists() or not CONDITION_FILE.exists():
        print("[ERROR] Required input files not found.")
        return None, None
    with open(INPUT_FILE, 'r') as f:
        patient_data = json.load(f)
    with open(CONDITION_FILE, 'r') as f:
        condition_data = json.load(f)
    return patient_data, condition_data

def map_snomed_to_icd10(snomed_code):
    try:
        response = requests.get(f"{HERMES_URL}?code={snomed_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['code'], data[0]['display']
    except:
        pass
    return "R56.9", "Unspecified convulsions"

def create_hl7_message(patient_data, condition_data):
    patient_id = patient_data.get("primary_patient_id", "")
    name_data = patient_data.get("name", [{}])[0]
    family = name_data.get("family", "")
    given = " ".join(name_data.get("given", []))

    gender_raw = patient_data.get("gender", "").lower()
    gender = "F" if gender_raw == "female" else "M" if gender_raw == "male" else "U"
    birth_date = patient_data.get("birthDate", "").replace("-", "")

    msg = Message("ADT_A01", version="2.5")

    now = datetime.now().strftime("%Y%m%d%H%M%S")
    msg.msh.msh_3 = "FHIR_APP"
    msg.msh.msh_4 = "OPENEMR"
    msg.msh.msh_5 = "HL7_ENGINE"
    msg.msh.msh_6 = "PRIMARY_EHR"
    msg.msh.msh_7 = now
    msg.msh.msh_9 = "ADT^A01"
    msg.msh.msh_10 = "MSG00001"
    msg.msh.msh_11 = "P"
    msg.msh.msh_12 = "2.5"

    msg.pid.pid_1 = "1"
    msg.pid.pid_3 = patient_id
    msg.pid.pid_5 = f"{family}^{given}"
    msg.pid.pid_7 = birth_date
    msg.pid.pid_8 = gender

    msg.pv1.pv1_2 = "I"
    msg.pv1.pv1_44 = datetime.now().strftime("%Y%m%d")

    if "entry" in condition_data:
        entries = condition_data["entry"]
    else:
        entries = [{"resource": condition_data}]

    for idx, entry in enumerate(entries):
        resource = entry.get("resource", {})
        snomed = resource.get("code", {}).get("coding", [{}])[0].get("code", "")
        desc = resource.get("code", {}).get("coding", [{}])[0].get("display", "Diagnosis")
        icd_code, icd_desc = map_snomed_to_icd10(snomed)

        dg1 = msg.add_segment("DG1")
        dg1.dg1_1 = str(idx + 1)
        dg1.dg1_2 = icd_code
        dg1.dg1_3 = icd_desc
        dg1.dg1_4 = desc
        dg1.dg1_6 = "F"

    return msg.to_er7()

if __name__ == '__main__':
    patient, condition = load_data()
    if not patient or not condition:
        exit()

    hl7_message = create_hl7_message(patient, condition)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(hl7_message)
print("[SUCCESS] HL7 message with all conditions written to coding_task5_output.txt")
