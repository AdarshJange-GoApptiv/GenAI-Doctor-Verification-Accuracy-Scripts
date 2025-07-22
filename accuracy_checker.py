import re
import logging
from difflib import SequenceMatcher
from master_data_utils import get_speciality_master, get_qualification_master, match_with_alias
from fuzzywuzzy import fuzz

speciality_master = get_speciality_master()
qualification_master = get_qualification_master()

logging.debug(f"Loaded {len(speciality_master)} specialities from master.")
print(f"Loaded {len(speciality_master)} specialities from master.")
logging.debug(f"Loaded {len(qualification_master)} qualifications from master.")
print(f"Loaded {len(qualification_master)} qualifications from master.")

def normalize(val):
    return (val or "").strip().lower()

def normalize_mobile(val):
    val = re.sub(r"\s+", "", str(val))
    if val.startswith("+91"):
        val = val[3:]
    elif val.startswith("91") and len(val) > 10:
        val = val[2:]
    return val[-10:]  # Ensure last 10 digits (mobile)

def fuzzy_match(str1, str2, threshold=0.8):
    return SequenceMatcher(None, normalize(str1), normalize(str2)).ratio() >= threshold

# ------------------------------
# Name
# ------------------------------
def check_name_match(row, extracted):
    result = {}
    excel_name = normalize(row.get("doctorName", ""))
    mongo_name = normalize(extracted.get("name", ""))
    name_match = fuzzy_match(excel_name, mongo_name)

    result["name_excel"] = excel_name
    result["name_mongo"] = mongo_name
    result["name_match"] = int(name_match)

    logging.debug(f"[Name] Excel: '{excel_name}' | Mongo: '{mongo_name}' | Match: {name_match}")
    return result, int(name_match), 1

# ------------------------------
# Contacts
# ------------------------------
def check_contacts_match(row, extracted):
    result = {}
    match_count = 0
    total = 0

    contacts_raw = str(row.get("contacts", ""))
    contact_list = [c.strip() for c in contacts_raw.split("|") if c.strip()]
    mongo_contacts = {
        normalize_mobile(extracted.get("mobile", "")),
        normalize_mobile(extracted.get("mobile_original", ""))
    }

    for i, contact in enumerate(contact_list):
        excel_contact = normalize_mobile(contact)
        is_match = excel_contact in mongo_contacts

        result[f"contact_excel_{i+1}"] = excel_contact
        result[f"contact_mongo_{i+1}"] = ', '.join(mongo_contacts)
        result[f"contact_match_{i+1}"] = int(is_match)

        logging.debug(f"[Contact {i+1}] Excel: {excel_contact} | Mongo: {mongo_contacts} | Match: {is_match}")

        match_count += int(is_match)
        total += 1

    return result, match_count, total

# ------------------------------
# Qualifications
# ------------------------------
def check_qualifications_match(row, extracted):
    result = {}
    match_count = 0
    total = 0

    qualification_str = row.get("Qualifications", "") or row.get("qualifications", "")
    qual_list = [q.strip() for q in qualification_str.split("|") if q.strip()]
    mongo_quals = extracted.get("qualification_values", [])

    for i, q in enumerate(qual_list):
        excel_q = normalize(q)
        is_match = False
        matched_mongo = ""

        if mongo_quals:
            mongo_quals_norm = [normalize(mq) for mq in mongo_quals]
            matched_mongo = next((mq for mq in mongo_quals_norm if excel_q in mq or mq in excel_q), "")

            if matched_mongo:
                is_match = True

            # No direct match, check aliases
            if not is_match:
                for mq in mongo_quals_norm:
                    if match_with_alias(excel_q, mq, qualification_master):
                        matched_mongo = mq
                        is_match = True
                        break
        else:
            # If no data in MongoDB, consider it 100% match
            matched_mongo = "{}"
            is_match = True

        result[f"qualification_excel_{i+1}"] = excel_q
        result[f"qualification_mongo_{i+1}"] = matched_mongo
        result[f"qualification_match_{i+1}"] = int(is_match)

        match_count += int(is_match)
        total += 1

    return result, match_count, total


# ------------------------------
# Specialities
# ------------------------------
def check_specialities_match(row, extracted):
    result = {}
    match_count = 0
    total = 0

    speciality_str = row.get("Specialities", "") or row.get("specialities", "")
    spec_list = [s.strip() for s in speciality_str.split("|") if s.strip()]
    mongo_specs = extracted.get("speciality_values", [])

    for i, s in enumerate(spec_list):
        excel_s = normalize(s)
        is_match = False
        matched_mongo = ""

        if mongo_specs:
            mongo_specs_norm = [normalize(ms) for ms in mongo_specs]
            matched_mongo = next((ms for ms in mongo_specs_norm if fuzz.ratio(excel_s, ms) >= 95), "")

            if matched_mongo:
                is_match = True

            # No fuzzy match, check aliases
            if not is_match:
                for ms in mongo_specs_norm:
                    if match_with_alias(excel_s, ms, speciality_master):
                        matched_mongo = ms
                        is_match = True
                        break
        else:
            # No data in MongoDB, consider accurate
            matched_mongo = "{}"
            is_match = True

        result[f"speciality_excel_{i+1}"] = excel_s
        result[f"speciality_mongo_{i+1}"] = matched_mongo
        result[f"speciality_match_{i+1}"] = int(is_match)

        match_count += int(is_match)
        total += 1

    return result, match_count, total

# ------------------------------
# Main Accuracy Function
# ------------------------------
def compare_fields(row, extracted):
    if extracted["status"] != "success":
        return {
            "accuracy_percent": 0,
            "status": extracted["status"],
            "error_message": extracted.get("message", "") or str(extracted.get("errors", ""))
        }

    result = {}
    total_matches = 0
    total_checks = 0

    for checker in [check_name_match, check_contacts_match, check_qualifications_match, check_specialities_match]:
        try:
            check_result, matches, total = checker(row, extracted)
            result.update(check_result)
            total_matches += matches
            total_checks += total
        except Exception as e:
            logging.warning(f"[{checker.__name__}] Error: {e}")

    # Accuracy %
    accuracy_percent = round((total_matches / total_checks) * 100, 2) if total_checks else 0
    result["accuracy_percent"] = accuracy_percent
    result["status"] = "success"

    logging.info(f"Final Accuracy: {accuracy_percent}% ({total_matches}/{total_checks} matched)")
    return result
