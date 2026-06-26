import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  
CSV_PATH = str(BASE_DIR / "doctor_availability.csv")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"
TEMPERATURE = 0

VALID_SPECIALIZATIONS = [
    "general_dentist",
    "oral_surgeon",
    "orthodontist",
    "cosmetic_dentist",
    "prosthodontist",
    "pediatric_dentist",
    "emergency_dentist",
]

VALID_DOCTORS = [
    "john doe",
    "emily johnson",
    "sarah wilson",
    "jane smith",
    "michael green",
    "robert martinez",
    "lisa brown",
    "susan davis",
    "daniel miller",
    "kevin anderson",
]

DATE_FORMAT = "%m/%d/%Y %H:%M"


