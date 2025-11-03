# import sys
# import os

# # Add project root to sys.path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import db_config
from .test_models import (
    TestClient, 
    TestPlan, 
    TestPayment,
    TestSubscription,
    TestVisit,
)

# DB_NAME = db_config.TEST_DB_NAME

# if not DB_NAME:
#     raise Exception('Database name not provided. Please check env.')

# # Monkey-patch the default before creating inone_subscription.assigned_users[0].client_idstances
# Client.__init__ = lambda self, using=None: super(Client, self).__init__(using=DB_NAME)

# TestClient.start_test()
# TestPlan.start_test()
# TestPayment.start_test()
# TestSubscription.start_test()
TestVisit.start_test()

