from dotenv import load_dotenv
import os

load_dotenv()


DB_NAME = os.getenv('DB_NAME')

TEST_DB_NAME = f'test_{DB_NAME}'

