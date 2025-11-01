import time
from configs import db_config, app_config
from database.db import InitDB
from models.client import Client
from models.plan import Plan
from models.payment import Payment
from models.subscription import Subscription
from models.visit import Visit
from models.assigned_client import AssignedClient
from helpers.db_helpers import delete_db
import os
# import sqlite3

from .test_data import (
    clients as clients_data,
    plans as plans_data,
    payments as payments_data
)


DB_NAME = db_config.TEST_DB_NAME

# InitDB(using=DB_NAME)

if not DB_NAME:
    raise Exception('Database name not provided. Please check env.')

delete_db(app_config.BASE_DIR, DB_NAME)

# Monkey-patch the default before creating instances
# Client.__init__ = lambda self, using=None: super(Client, self).__init__(using=DB_NAME)


def get_client():
    for client in clients_data:
        yield client

def get_plan():
    for plan in plans_data:
        yield plan

def get_payments():
    for payment in payments_data:
        yield payment

    

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
        cls._test_import_pdf(cls)

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

        filter_by_date = Client.filter_client('2025', by_date=True, using=DB_NAME)
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
        assert os.path.isfile(app_config.BASE_DIR / 'tests/clients_export.pdf')
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
        path = app_config.BASE_DIR / 'tests/clients_export.pdf'
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
        cls._test_fetch_plans(cls)
        cls._test_update_plan(cls)
        cls._test_delete_plan(cls)
        cls._test_export_csv(cls)
        cls._test_export_xlsx(cls)
        cls._test_export_pdf(cls)
        cls._test_delete_all_plans(cls)
        cls._test_import_csv(cls)
        cls._test_import_xlsx(cls)
        cls._test_import_pdf(cls)

    def _test_create_plan(self):
        print('\nTest 1: Creating plans from test data')

        for plan in get_plan():
            new_plan = Plan(kwargs=plan, using=DB_NAME)
            new_plan.get_id()
            new_plan.save_to_db()
            # time.sleep(5)

        print('Test 1: Passed ✅')

    def _test_fetch_plans(self):
        print('\nTest 2: Fetching plans from DB')

        fetched_plans = Plan.fetch_all(using=DB_NAME)
        assert len(fetched_plans) > 0

        one_plan = Plan.fetch_one(fetched_plans[1].plan_id, using=DB_NAME)
        assert one_plan.plan_name == '5 Slot'
        assert one_plan.duration == 5
        assert one_plan.price == 29000

        filter_by_name = Plan.filter_plan('daily', plan_type=True, using=DB_NAME)
        assert len(filter_by_name) > 0

        filter_by_date = Plan.filter_plan('2025', by_date=True, using=DB_NAME)
        assert len(filter_by_date) > 0

        print('Test 2: Passed ✅')

    def _test_update_plan(self):
        print('\nTest 3: Updating plans in DB')

        fetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]
        
        one_plan.plan_name = 'Updated 1 Slot'

        one_plan.update()
    
        one_plan_refetched = Plan.fetch_one(one_plan.plan_id, using=DB_NAME)

        assert one_plan_refetched.plan_name == one_plan.plan_name

        print('Test 3: Passed ✅')

    def _test_delete_plan(self):
        print('\nTest 4: Delete plans in DB')

        fetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]

        one_plan.delete()
    
        one_plan_refetched = Plan.fetch_one(one_plan.plan_id, using=DB_NAME)

        assert one_plan_refetched is None

        print('Test 4: Passed ✅')

    def _test_export_csv(self):
        print('\nTest 5: Export plans to csv')
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.csv', path, using=DB_NAME)
        assert os.path.isfile(path / 'plans_export.csv')
        print('Test 5: Passed ✅')

    def _test_export_xlsx(self):
        print('\nTest 6: Export plans to xlsx')
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.xlsx', path, using=DB_NAME)
        assert os.path.isfile(path / 'plans_export.xlsx')
        print('Test 6: Passed ✅')

    def _test_export_pdf(self):
        print('\nTest 7: Export plans to pdf')
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.pdf', path, using=DB_NAME)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/plans_export.pdf')
        print('Test 7: Passed ✅')

    def _test_delete_all_plans(self):
        print('\nTest 8: Delete all plans in DB')

        fetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(fetched_plans) > 0

        for client in fetched_plans:
            client.delete()

        refetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(refetched_plans) == 0

        print('Test 8: Passed ✅')

    def _test_import_csv(self):
        print('\nTest 9: Importing plans from csv')
        path = app_config.BASE_DIR / 'tests/plans_export.csv'
        Plan.import_plans(path, '.csv', has_header=True, using=DB_NAME)

        fetched_plans = Plan.fetch_all(using=DB_NAME)
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(refetched_plans) == 0

        print('Test 9: Passed ✅')

    def _test_import_xlsx(self):
        print('\nTest 10: Importing plans from xlsx')
        path = app_config.BASE_DIR / 'tests/plans_export.xlsx'
        Plan.import_plans(path, '.xlsx', has_header=True, using=DB_NAME)

        fetched_plans = Plan.fetch_all(using=DB_NAME)
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(refetched_plans) == 0

        print('Test 10: Passed ✅')

    def _test_import_pdf(self):
        print('\nTest 11: Importing plans from pdf')
        path = app_config.BASE_DIR / 'tests/plans_export.pdf'
        Plan.import_plans(path, '.pdf', has_header=True, using=DB_NAME)

        fetched_plans = Plan.fetch_all(using=DB_NAME)
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all(using=DB_NAME)

        assert len(refetched_plans) == 0

        print('Test 11: Passed ✅')
 

class TestPayment:

    @classmethod
    def start_test(cls):
        print(f'Initializing Payment Model with {Payment(using=DB_NAME)._db}...')

        cls._test_create_payments(cls)
        cls._test_fetch_payments(cls)
        cls._test_update_payment(cls)
        cls._test_delete_payment(cls)

    def _test_create_payments(self):
        print('\nTest 1: Creating payments from test data')

        for payment in get_payments():
            new_payment = Payment(kwargs=payment, using=DB_NAME)
            new_payment.get_id()
            new_payment.save_to_db()
            # time.sleep(5)

        print('Test 1: Passed ✅')

    def _test_fetch_payments(self):
        print('\nTest 2: Fetching payments from DB')

        fetched_payments = Payment.fetch_all(using=DB_NAME)
        assert len(fetched_payments) > 0

        one_payment = Payment.fetch_one(fetched_payments[1].payment_id, using=DB_NAME)
        assert one_payment.tax == 7.5
        assert one_payment.total_price == 6000.0
        assert one_payment.amount_paid == 6000.0

        filter_by_amount = Payment.filter_payments(6000, by_amount=True, using=DB_NAME)
        assert len(filter_by_amount) > 0

        filter_by_date = Payment.filter_payments('2025', by_date=True, using=DB_NAME)
        assert len(filter_by_date) > 0

        print('Test 2: Passed ✅')

    def _test_update_payment(self):
        print('\nTest 3: Updating payment in DB')

        fetched_payment = Payment.fetch_all(using=DB_NAME)

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]
        
        one_payment.discount = 10

        one_payment.update()
    
        one_payment_refetched = Payment.fetch_one(one_payment.payment_id, using=DB_NAME)

        assert one_payment_refetched.discount == one_payment.discount

        print('Test 3: Passed ✅')

    def _test_delete_payment(self):
        print('\nTest 4: Delete payment in DB')

        fetched_payment = Payment.fetch_all(using=DB_NAME)

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]

        one_payment.delete()
    
        one_payment_refetched = Payment.fetch_one(one_payment.payment_id, using=DB_NAME)

        assert one_payment_refetched is None

        print('Test 4: Passed ✅')

   

