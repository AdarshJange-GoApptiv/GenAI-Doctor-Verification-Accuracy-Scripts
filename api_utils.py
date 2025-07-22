import requests
import uuid
import logging
from config import API_URL, CATEGORY, FLOW_ID, API_HEADERS

def generate_reference_id(image_uuid, version="v1"):
    suffix = uuid.uuid4().hex[:4]
    return f"{image_uuid}_{version}_{suffix}"

def call_extraction_api(image_uuid, reference_id):
    payload = {
        "category": CATEGORY,
        "flowId": FLOW_ID,
        "referenceId": reference_id,
        "flowInputData": {
            "id": image_uuid
        }
    }

    try:
        response = requests.post(API_URL, json=payload, headers=API_HEADERS, timeout=10)
        status_code = response.status_code
        response_json = response.json()

        if status_code in [200, 202]:
            logging.info(f" API call success for {image_uuid} -> {reference_id}")
        else:
            logging.warning(
                f" API returned {status_code} for {image_uuid} -> {reference_id}: {response.text}"
            )

        return status_code, response_json

    except Exception as e:
        logging.error(f" API call failed for {image_uuid} -> {reference_id}: {e}")
        return 500, {"error": str(e)}
