from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
import time
import logging

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

def get_raw_extraction_document(reference_id):
    """
    Get the raw document from MongoDB for given referenceId.
    """
    logging.debug(f"Querying MongoDB with referenceId: {reference_id}")
    result = collection.find_one({"referenceId": reference_id})
    if result:
        logging.info(f"Document found in MongoDB for {reference_id}")
    else:
        logging.debug(f"No document found yet for {reference_id}")
    return result



def get_extracted_fields(doc):
    if doc.get("status") == "failed":
        return {
            "status": "failed",
            "errors": doc.get("errorMessages", [])
        }

    try:
        doctors = doc.get("data", {}).get("doctors", [])
        if not doctors:
            return {
                "status": "parsing_error",
                "message": "No doctor data found"
            }

        doctor = doctors[0]
        result = {"status": "success"}

        # Name
        name_info = doctor.get("name", {})
        result["name"] = name_info.get("value", "")

        # Mobile (handle missing or empty list)
        mobile_numbers = doctor.get("mobileNumbers", [])
        mobile_info = mobile_numbers[0] if mobile_numbers else {}
        result["mobile"] = mobile_info.get("value", "")
        result["mobile_original"] = mobile_info.get("value", "")

        # Qualifications (LIST — use value for matching)
        qualifications = doctor.get("qualifications", [])
        # print(f"Qualifications: {qualifications}")
        result["qualification_values"] = [q.get("value", "") for q in qualifications if q.get("value")]

        # Specialities (LIST — use value for matching)
        specialities = doctor.get("specialities", [])
        # print(f"Specialities: {specialities}")
        result["speciality_values"] = [s.get("value", "") for s in specialities if s.get("value")]


        logging.debug(f"Extracted Name: {result['name']}")
        logging.debug(f"Extracted Mobiles: {result['mobile']}, {result['mobile_original']}")
        logging.debug(f"Extracted Qualifications: {result['qualification_values']}")
        logging.debug(f"Extracted Specialities: {result['speciality_values']}")

        logging.debug(f"[Extracted Fields] Returning: {result}")

        return result

    except Exception as e:
        return {
            "status": "parsing_error",
            "message": f"Extraction parsing failed: {str(e)}"
        }



def wait_for_extraction_result(reference_id, retries=12, delay=10):
    """
    Waits and retries fetching the Mongo document by referenceId.
    Logs each retry attempt.
    """
    for attempt in range(1, retries + 1):
        doc = get_raw_extraction_document(reference_id)
        if doc:
            logging.info(f"Mongo document found for {reference_id} on attempt {attempt}")
            return doc
        logging.info(f"Retry {attempt}/{retries} - Waiting for MongoDB record for {reference_id}")
        time.sleep(delay)

    logging.warning(f"No Mongo document found after {retries} retries for {reference_id}")
    return None
