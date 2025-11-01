from dotenv import load_dotenv
import os

load_dotenv()


DB_NAME = os.getenv('DB_NAME')

TEST_DB_NAME = os.getenv('TEST_DB_NAME')

