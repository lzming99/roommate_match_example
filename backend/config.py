import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    DB_NAME = "first_try"