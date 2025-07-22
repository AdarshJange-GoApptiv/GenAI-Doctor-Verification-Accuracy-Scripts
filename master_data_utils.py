import requests
import logging
from fuzzywuzzy import fuzz

# Configure logging once globally
logging.basicConfig(
    filename='accuracy_debug.log',  # Logs will go here
    filemode='a',  # Append to the file
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


SPECIALITY_MASTER_URL = "https://masters.goapptiv.one/api/v1/specialities"
QUALIFICATION_MASTER_URL = "https://masters.goapptiv.one/api/v1/qualifications"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9uZWdvYXBwdGl2X21tIn0.eyJ1c2VybmFtZSI6Ik9ORUdPQVBQVElWX09GRkVSTUdNVCIsImlzQWRtaW4iOnRydWUsImlhdCI6MTY2NDg3NjY5Nn0.l_1Bap6_5X2FmYLVanaGmieHKTxjmO8-dpc2eMgMX3o"

HEADERS = {
    "Authorization": AUTH_TOKEN
}

def fetch_master_data(url):
    headers = {
        "Authorization": AUTH_TOKEN
    }
    try:
        logging.info(f"Fetching master data from URL: {url}")
        print(f"Fetching master data from URL: {url}")

        response = requests.get(url, headers=HEADERS)
        logging.debug(f"API Response Code: {response.status_code}")
        logging.debug(f"API Response Body: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            logging.info(f"Fetched {len(data)} items from {url}")
            print(f"Fetched {len(data)} items from {url}")
            # return data
            items = data.get("data") or data.get("result") or data

            valid_items = []
            for item in items:
                if isinstance(item, dict) and "name" in item:
                    valid_items.append({
                        "name": item.get("name", "").strip(),
                        "aliases": [a.strip() for a in item.get("aliases", []) if a]
                    })
                else:
                    logging.warning(f"Skipping invalid master item: {item}")

            logging.info(f"Parsed {len(valid_items)} valid items from {url}")
            return valid_items
        else:
            logging.error(f"Failed to fetch from {url}. Status code: {response.status_code}")
            print(f"Failed to fetch from {url}. Status code: {response.status_code}")
    except Exception as e:
        logging.exception(f"Exception while fetching master data from {url}: {e}")
        print(f"Exception while fetching master data from {url}: {e}")
    return []

def get_speciality_master():
    return fetch_master_data(SPECIALITY_MASTER_URL)

def get_qualification_master():
    return fetch_master_data(QUALIFICATION_MASTER_URL)

def match_with_alias(input_value, extracted_value, master_data, use_fuzzy=False, fuzzy_threshold=95):
    try:
        input_value = str(input_value or "").lower().strip()
        extracted_value = str(extracted_value or "").lower().strip()

        for item in master_data:
            name = item.get("name", "")
            aliases = item.get("aliases", [])

            name = str(name).lower().strip()
            aliases = [str(alias).lower().strip() for alias in aliases]

            all_names = [name] + aliases

            if input_value in all_names and extracted_value in all_names:
                logging.debug(f"[match_with_alias] Match found: '{input_value}' ↔ '{extracted_value}' using aliases.")
                return True
            
        if use_fuzzy:
            similarity = fuzz.token_sort_ratio(input_value, extracted_value)
            logging.debug(f"[Fuzzy Check] {input_value} <-> {extracted_value} | Similarity: {similarity}")
            if similarity >= fuzzy_threshold:
                logging.debug(f"[Fuzzy Match] {input_value} <-> {extracted_value} | Similarity: {similarity}")
                return True

        logging.debug(f"[match_with_alias] No match for: '{input_value}' ↔ '{extracted_value}'")
        return False

    except Exception as e:
        logging.error(f"[match_with_alias] Exception occurred: {e}")
        return False
