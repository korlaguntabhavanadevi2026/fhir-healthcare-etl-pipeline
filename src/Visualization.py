import json
import requests
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path.cwd() / "data"
FHIR_BASE_URL = "https://in-info-web20.luddy.indianapolis.iu.edu/apis/default/fhir"

def load_token():
    token_file = DATA_DIR / "access_token.json"
    try:
        with open(token_file) as f:
            return json.load(f)["access_token"]
    except Exception as e:
        print(f"Token load error: {e}")
        return None

def get_headers():
    token = load_token()
    if not token:
        return None
    return {"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"}

def fetch_patients():
    url = f"{FHIR_BASE_URL}/Patient"
    patients = []
    headers = get_headers()

    while url and headers:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            patients += data.get("entry", [])
            url = next((l["url"] for l in data.get("link", []) if l["relation"] == "next"), None)
        else:
            print("Error:", response.status_code)
            break
    return patients

def plot_gender_distribution():
    patients = fetch_patients()
    counts = {"male": 0, "female": 0}

    for p in patients:
        gender = p["resource"].get("gender", "").lower()
        if gender in counts:
            counts[gender] += 1
        else:
            counts["other"] += 1

    genders = list(counts.keys())
    values = list(counts.values())

    plt.figure(figsize=(7, 5))
    plt.bar(genders, values, color=['skyblue', 'lightpink', 'gray'])
    plt.title("Patient Gender Distribution")
    plt.xlabel("Gender")
    plt.ylabel("Count")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
    ASSETS_DIR.mkdir(exist_ok=True)
    save_path = ASSETS_DIR / "gender_distribution.png"
    plt.savefig(save_path)
    print(f"Saved chart to: {save_path.resolve()}")

    plt.show()

if __name__ == "__main__":
    plot_gender_distribution()
