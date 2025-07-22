# Excel Config
EXCEL_INPUT_PATH = r"C:\Users\Naba Missong\Desktop\GA_WELLNESS Visiting Card images.xlsx"
# EXCEL_INPUT_PATH = "C:\\Users\\Naba Missong\\Desktop\\GA_WELLNESS Visiting Card images.xlsx"
# EXCEL_INPUT_PATH = "C:/Users/Naba Missong/Desktop/GA_WELLNESS Visiting Card images.xlsx"
EXCEL_OUTPUT_PATH = "output_accuracy_report.xlsx"
REFERENCE_ID_OUTPUT_PATH = "output_reference_ids2.xlsx"
 
import logging

API_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9uZWdvYXBwdGl2X2RvY3VtZW50X2RhdGFfZXh0cmFjdG9yIn0.eyJzdWIiOiI2NzFhMGM2M2Y4ZDliZTc3NDliMzkwNWUiLCJ1c2VybmFtZSI6ImNvZF9kb2N0b3JfbWFuYWdlbWVudCIsImlzQWRtaW4iOmZhbHNlLCJpYXQiOjE3NTExMTU1MzF9.gidsRchshWt6e_Axek8mG2kmRgYZD6DsBKN5K9zhGNY",  
    "Content-Type": "application/json"
}


# API Config
API_URL = "https://document-data-extractor-nestjs-staging-137541097606.asia-south1.run.app/api/v1/extractions"
# FLOW_ID = "685fe6246e65f83cdccf4b76"
FLOW_ID = "68788a7d4117941c39f31179"
CATEGORY = "doctor_visiting_card"


# Logging
LOG_FILE = "process.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
