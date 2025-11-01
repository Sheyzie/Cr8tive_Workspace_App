# import sys
# import os

# # Add project root to sys.path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import db_config
from .test_models import TestClient, TestPlan
from models.client import Client

# DB_NAME = db_config.TEST_DB_NAME

# if not DB_NAME:
#     raise Exception('Database name not provided. Please check env.')

# # Monkey-patch the default before creating instances
# Client.__init__ = lambda self, using=None: super(Client, self).__init__(using=DB_NAME)

# client = Client()
# print(client._db)  # test

TestClient.start_test()
TestPlan.start_test()
