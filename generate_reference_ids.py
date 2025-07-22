# generate_reference_ids.py

import time
import logging
from config import EXCEL_INPUT_PATH, REFERENCE_ID_OUTPUT_PATH
from excel_utils import read_image_uuid_and_truth, write_reference_ids
from api_utils import call_extraction_api, generate_reference_id

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Starting GenAI API Reference ID Generation...")

    records = read_image_uuid_and_truth(EXCEL_INPUT_PATH)
    output_rows = []

    for index, row in enumerate(records):
        image_uuid = row["imageUuid"]
        reference_id = generate_reference_id(image_uuid, version="v1")

        # Make the API call
        status_code, _ = call_extraction_api(image_uuid, reference_id)

        if status_code == 200:
            logging.info(f"API call success for {image_uuid} -> {reference_id}")
        else:
            logging.warning(f"API call failed for {image_uuid} -> {reference_id}")

        # Save reference_id regardless of API success
        output_rows.append({
            "imageUuid": image_uuid,
            "reference_id": reference_id
        })

        # Wait 1 minutes before next call
        if index < len(records) - 1:
            logging.info("Waiting 1 minutes before next API call...")
            time.sleep(60)

    # Save to Excel
    write_reference_ids(output_rows, REFERENCE_ID_OUTPUT_PATH)
    logging.info(f"Reference ID generation complete. Output saved to {REFERENCE_ID_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
