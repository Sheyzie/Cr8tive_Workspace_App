import time
from configs import db_config, app_config
from database.db import InitDB
from models.client import Client
from models.plan import Plan
from models.payment import Payment
from models.subscription import Subscription
from models.visit import Visit
from models.assigned_client import AssignedClient
import os
# import sqlite3

from .test_data import clients as clients_data


DB_NAME = db_config.TEST_DB_NAME

# InitDB(using=DB_NAME)

if not DB_NAME:
    raise Exception('Database name not provided. Please check env.')

# Monkey-patch the default before creating instances
# Client.__init__ = lambda self, using=None: super(Client, self).__init__(using=DB_NAME)


def get_client():
    for client in clients_data:
        yield client

def get_plan():
    for plan in plan_data:
        yield plan

class TestClient:

    @classmethod
    def start_test(cls):
        print(f'Initializing Client Model with {Client(using=DB_NAME)._db}...')

        cls._test_create_client(cls)
        cls._test_fetch_client(cls)
        cls._test_update_client(cls)
        cls._test_delete_client(cls)
        cls._test_export_csv(cls)
        cls._test_export_xlsx(cls)
        cls._test_export_pdf(cls)
        cls._test_delete_all_clients(cls)
        cls._test_import_csv(cls)
        cls._test_import_xlsx(cls)

    def _test_create_client(self):
        print('\nTest 1: Creating clients from test data')

        for client in get_client():
            new_client = Client(kwargs=client, using=DB_NAME)
            new_client.get_id()
            new_client.save_to_db()
            # time.sleep(5)

        print('Test 1: Passed ✅')

    def _test_fetch_client(self):
        print('\nTest 2: Fetching clients from DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        one_client = Client.fetch_one(fetched_clients[1].client_id, using=DB_NAME)
        assert one_client.first_name == 'Client'

        filter_by_name = Client.filter_client('Client', name=True, using=DB_NAME)
        assert len(filter_by_name) > 0

        filter_by_date = Client.filter_client('2025', created_at=True, using=DB_NAME)
        assert len(filter_by_date) > 0

        print('Test 2: Passed ✅')

    def _test_update_client(self):
        print('\nTest 3: Updating clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]
        
        one_client.first_name = 'Updated Client'

        one_client.update()
    
        one_client_refetched = Client.fetch_one(one_client.client_id, using=DB_NAME)

        assert one_client_refetched.first_name == one_client.first_name

        print('Test 3: Passed ✅')

    def _test_delete_client(self):
        print('\nTest 4: Delete clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        one_client.delete()
    
        one_client_refetched = Client.fetch_one(one_client.client_id, using=DB_NAME)

        assert one_client_refetched is None

        print('Test 4: Passed ✅')

    def _test_export_csv(self):
        print('\nTest 5: Export clients to csv')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.csv', path, using=DB_NAME)
        assert os.path.isfile(path / 'clients_export.csv')
        print('Test 5: Passed ✅')

    def _test_export_xlsx(self):
        print('\nTest 6: Export clients to xlsx')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.xlsx', path, using=DB_NAME)
        assert os.path.isfile(path / 'clients_export.xlsx')
        print('Test 6: Passed ✅')

    def _test_export_pdf(self):
        print('\nTest 7: Export clients to pdf')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.pdf', path, using=DB_NAME)
        assert os.path.isfile(app_config.BASE_DIR / 'clients_export.pdf')
        print('Test 7: Passed ✅')

    def _test_delete_all_clients(self):
        print('\nTest 8: Delete all clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 8: Passed ✅')

    def _test_import_csv(self):
        print('\nTest 9: Importing clients from csv')
        path = app_config.BASE_DIR / 'tests/clients_export.csv'
        Client.import_clients(path, '.csv', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 9: Passed ✅')

    def _test_import_xlsx(self):
        print('\nTest 10: Importing clients from xlsx')
        path = app_config.BASE_DIR / 'tests/clients_export.xlsx'
        Client.import_clients(path, '.xlsx', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 10: Passed ✅')

    def _test_import_pdf(self):
        print('\nTest 11: Importing clients from pdf')
        path = app_config.BASE_DIR / 'clients_export.pdf'
        Client.import_clients(path, '.pdf', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 11: Passed ✅')
 

class TestPlan:

    @classmethod
    def start_test(cls):
        print(f'Initializing Plan Model with {Plan(using=DB_NAME)._db}...')

        cls._test_create_plan(cls)
        # cls._test_fetch_plan(cls)
        # cls._test_update_plan(cls)
        # cls._test_delete_plan(cls)
        # cls._test_export_csv(cls)
        # cls._test_export_xlsx(cls)
        # cls._test_export_pdf(cls)
        # cls._test_delete_all_plans(cls)
        # cls._test_import_csv(cls)
        # cls._test_import_xlsx(cls)

    def _test_create_plan(self):
        print('\nTest 1: Creating plans from test data')

        for plan in get_plan():
            new_plan = Plan(kwargs=plan, using=DB_NAME)
            new_plan.get_id()
            new_plan.save_to_db()
            # time.sleep(5)

        print('Test 1: Passed ✅')

    def _test_fetch_plan(self):
        print('\nTest 2: Fetching plans from DB')

        fetched_plans = Plan.fetch_all(using=DB_NAME)
        assert len(fetched_plans) > 0

        one_plan = Plan.fetch_one(fetched_plans[1].plan_id, using=DB_NAME)
        assert one_plan.plan_name == '1 Slot'

        filter_by_name = Plan.filter_plan('Plan', name=True, using=DB_NAME)
        assert len(filter_by_name) > 0

        filter_by_date = Plan.filter_plan('2025', created_at=True, using=DB_NAME)
        assert len(filter_by_date) > 0

        print('Test 2: Passed ✅')

    def _test_update_client(self):
        print('\nTest 3: Updating clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]
        
        one_client.first_name = 'Updated Client'

        one_client.update()
    
        one_client_refetched = Client.fetch_one(one_client.client_id, using=DB_NAME)

        assert one_client_refetched.first_name == one_client.first_name

        print('Test 3: Passed ✅')

    def _test_delete_client(self):
        print('\nTest 4: Delete clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        one_client.delete()
    
        one_client_refetched = Client.fetch_one(one_client.client_id, using=DB_NAME)

        assert one_client_refetched is None

        print('Test 4: Passed ✅')

    def _test_export_csv(self):
        print('\nTest 5: Export clients to csv')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.csv', path, using=DB_NAME)
        assert os.path.isfile(path / 'clients_export.csv')
        print('Test 5: Passed ✅')

    def _test_export_xlsx(self):
        print('\nTest 6: Export clients to xlsx')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.xlsx', path, using=DB_NAME)
        assert os.path.isfile(path / 'clients_export.xlsx')
        print('Test 6: Passed ✅')

    def _test_export_pdf(self):
        print('\nTest 7: Export clients to pdf')
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.pdf', path, using=DB_NAME)
        assert os.path.isfile(app_config.BASE_DIR / 'clients_export.pdf')
        print('Test 7: Passed ✅')

    def _test_delete_all_clients(self):
        print('\nTest 8: Delete all clients in DB')

        fetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(fetched_clients) > 0

        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 8: Passed ✅')

    def _test_import_csv(self):
        print('\nTest 9: Importing clients from csv')
        path = app_config.BASE_DIR / 'tests/clients_export.csv'
        Client.import_clients(path, '.csv', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 9: Passed ✅')

    def _test_import_xlsx(self):
        print('\nTest 10: Importing clients from xlsx')
        path = app_config.BASE_DIR / 'tests/clients_export.xlsx'
        Client.import_clients(path, '.xlsx', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 10: Passed ✅')

    def _test_import_pdf(self):
        print('\nTest 11: Importing clients from pdf')
        path = app_config.BASE_DIR / 'clients_export.pdf'
        Client.import_clients(path, '.pdf', has_header=True, using=DB_NAME)

        fetched_clients = Client.fetch_all(using=DB_NAME)
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all(using=DB_NAME)

        assert len(refetched_clients) == 0

        print('Test 11: Passed ✅')
 

