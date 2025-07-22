import time
import logging
from config import REFERENCE_ID_OUTPUT_PATH, ACCURACY_OUTPUT_PATH
from reader import read_reference_ids
from writer import write_accuracy_report
from mongo_utils import wait_for_extraction_result, get_extracted_fields
from accuracy_checker import compare_fields

logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG to see your logs
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    
    logging.info("Starting GenAI Accuracy Evaluation from MongoDB...")

    records = read_reference_ids(REFERENCE_ID_OUTPUT_PATH)
    results = []

    for index, row in enumerate(records):
        logging.info(f"Checking accuracy for UUID: {row['imageUuid']} -> {row['reference_id']}")
        result = process_accuracy(row)
        logging.debug(f"Result keys for UUID {row['imageUuid']}: {list(result.keys())}")
        logging.debug(f"[Result Keys] {row['imageUuid']}: {list(result.keys())}")
        logging.debug(f"[Final Result Entry] {result}")
        results.append(result)

    write_accuracy_report(results, ACCURACY_OUTPUT_PATH)
    logging.info(f"Accuracy report saved to {ACCURACY_OUTPUT_PATH}")

def process_accuracy(row):
    image_uuid = row["imageUuid"]
    reference_id = row["reference_id"]

    mongo_doc = wait_for_extraction_result(reference_id, retries=6, delay=5)
    if not mongo_doc:
        logging.warning(f"No MongoDB document found for {reference_id}")
        return {
            "image_uuid": image_uuid,
            "reference_id": reference_id,
            "status": "api_failed",
            "accuracy_percent": 0,
            "remarks": "MongoDB record not found"
        }

    if mongo_doc.get("status") == "failed":
        logging.warning(f"GenAI extraction failed for {reference_id}")
        return {
            "image_uuid": image_uuid,
            "reference_id": reference_id,
            "status": "processing_failed",
            "accuracy_percent": 0,
            "remarks": "GenAI pipeline failure"
        }

    try:
        extracted_fields = get_extracted_fields(mongo_doc)
        accuracy = compare_fields(row, extracted_fields)

        return {
            "image_uuid": image_uuid,
            "reference_id": reference_id,
            "status": "success",
            **accuracy
        }
        # return write_accuracy_report(accuracy,'accuracy_report.xlsx')
    except Exception as e:
        logging.warning(f"Accuracy check failed for {reference_id}: {str(e)}")
        return {
            "image_uuid": image_uuid,
            "reference_id": reference_id,
            "status": "parsing_error",
            "accuracy_percent": 0,
            "remarks": f"Accuracy parse error: {str(e)}"
        }


if __name__ == "__main__":
    main()
