from configs import db_config, app_config
from models.client import Client
from models.plan import Plan
from models.subscription import Subscription
from models.payment import Payment
from models.visit import Visit
from models.assigned_client import AssignedClient
from datetime import datetime
import os
import sys
import time

from .test_data import (
    clients as clients_data,
    plans as plans_data,
    payments as payments_data
)


DB_NAME = db_config.TEST_DB_NAME

if not DB_NAME:
    raise Exception('Database name not provided. Please check env.')


def get_client():
    for client in clients_data:
        yield client

def get_plan():
    for plan in plans_data:
        yield plan

def get_payments():
    for payment in payments_data:
        yield payment


class BaseTestClass:
    stderr = sys.stderr
    stdout = sys.stdout
    current_year = str(datetime.now().year)
    

class TestClient(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.stdout.write(f'\nStarting client test...\n')
        cls.stdout.flush()

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
        self.stdout.write('\nTest 1: Creating clients from test data')
        self.stdout.flush()

        for client in get_client():
            new_client = Client(**client)
            new_client.get_id()
            new_client.save_to_db()
            # time.sleep(5)

        self.stdout.write('\nTest 1: Passed ✅\n')
        self.stdout.flush()

    def _test_fetch_client(self):
        self.stdout.write('\nTest 2: Fetching clients from DB\n')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        one_client = Client.fetch_one(fetched_clients[1].client_id)
        assert one_client.first_name == fetched_clients[1].first_name

        filter_by_name = Client.filter_client('Client', name=True)
        assert len(filter_by_name) > 0

        
        filter_by_date = Client.filter_client(self.current_year, by_date=True)
        assert len(filter_by_date) > 0

        self.stdout.write('\nTest 2: Passed ✅\n')
        self.stdout.flush()

    def _test_update_client(self):
        self.stdout.write('\nTest 3: Updating clients in DB\n')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]
        
        one_client.first_name = 'Updated Client'

        one_client.update()
    
        one_client_refetched = Client.fetch_one(one_client.client_id)

        assert one_client_refetched.first_name == one_client.first_name

        self.stdout.write('\nTest 3: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_client(self):
        self.stdout.write('\nTest 4: Delete clients in DB\n')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        one_client.delete()
    
        one_client_refetched = Client.fetch_one(one_client.client_id)

        assert one_client_refetched is None

        self.stdout.write('\nTest 4: Passed ✅\n')
        self.stdout.flush()

    def _test_export_csv(self):
        self.stdout.write('\nTest 5: Export clients to csv\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.csv', path)
        assert os.path.isfile(path / 'clients_export.csv')
        self.stdout.write('\nTest 5: Passed ✅\n')
        self.stdout.flush()

    def _test_export_xlsx(self):
        self.stdout.write('\nTest 6: Export clients to xlsx\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.xlsx', path)
        assert os.path.isfile(path / 'clients_export.xlsx')
        self.stdout.write('\nTest 6: Passed ✅\n')
        self.stdout.flush()

    def _test_export_pdf(self):
        self.stdout.write('\nTest 7: Export clients to pdf\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Client.export_clients('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/clients_export.pdf')
        self.stdout.write('\nTest 7: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_all_clients(self):
        self.stdout.write('\nTest 8: Delete all clients in DB\n')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.stdout.write('\nTest 8: Passed ✅\n')
        self.stdout.flush()

    def _test_import_csv(self):
        self.stdout.write('\nTest 9: Importing clients from csv\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/clients_export.csv'
        Client.import_clients(path, '.csv', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.stdout.write('\nTest 9: Passed ✅\n')
        self.stdout.flush()

    def _test_import_xlsx(self):
        self.stdout.write('\nTest 10: Importing clients from xlsx\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/clients_export.xlsx'
        Client.import_clients(path, '.xlsx', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.stdout.write('\nTest 10: Passed ✅\n')
        self.stdout.flush()

    def _test_import_pdf(self):
        self.stdout.write('\nTest 11: Importing clients from pdf\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/clients_export.pdf'
        Client.import_clients(path, '.pdf', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.stdout.write('\nTest 11: Passed ✅\n')
        self.stdout.flush()
 

class TestPlan(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.stdout.write(f'\nStarting plan test..\n')
        cls.stdout.flush()

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
        self.stdout.write('\nTest 1: Creating plans from test data\n')
        self.stdout.flush()

        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.get_id()
            new_plan.save_to_db()
            # time.sleep(5)

        self.stdout.write('Test 1: Passed ✅\n')
        self.stdout.flush()

    def _test_fetch_plans(self):
        self.stdout.write('\nTest 2: Fetching plans from DB\n')
        self.stdout.flush()

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        one_plan = Plan.fetch_one(fetched_plans[1].plan_id)
        assert one_plan.plan_name == fetched_plans[1].plan_name
        assert one_plan.duration == fetched_plans[1].duration
        assert one_plan.price == fetched_plans[1].price

        filter_by_name = Plan.filter_plan('daily', plan_type=True)
        assert len(filter_by_name) > 0

        filter_by_date = Plan.filter_plan(self.current_year, by_date=True)
        assert len(filter_by_date) > 0

        self.stdout.write('Test 2: Passed ✅\n')
        self.stdout.flush()

    def _test_update_plan(self):
        self.stdout.write('\nTest 3: Updating plans in DB\n')
        self.stdout.flush()

        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]
        
        one_plan.plan_name = 'Updated 1 Slot'

        one_plan.update()
    
        one_plan_refetched = Plan.fetch_one(one_plan.plan_id)

        assert one_plan_refetched.plan_name == one_plan.plan_name

        self.stdout.write('Test 3: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_plan(self):
        self.stdout.write('\nTest 4: Delete plans in DB\n')
        self.stdout.flush()

        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]

        one_plan.delete()
    
        one_plan_refetched = Plan.fetch_one(one_plan.plan_id)

        assert one_plan_refetched is None

        self.stdout.write('Test 4: Passed ✅\n')
        self.stdout.flush()

    def _test_export_csv(self):
        self.stdout.write('\nTest 5: Export plans to csv\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.csv', path)
        assert os.path.isfile(path / 'plans_export.csv')
        self.stdout.write('Test 5: Passed ✅\n')
        self.stdout.flush()

    def _test_export_xlsx(self):
        self.stdout.write('\nTest 6: Export plans to xlsx\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.xlsx', path)
        assert os.path.isfile(path / 'plans_export.xlsx')
        self.stdout.write('Test 6: Passed ✅\n')
        self.stdout.flush()

    def _test_export_pdf(self):
        self.stdout.write('\nTest 7: Export plans to pdf\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Plan.export_plans('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/plans_export.pdf')
        self.stdout.write('Test 7: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_all_plans(self):
        self.stdout.write('\nTest 8: Delete all plans in DB')
        self.stdout.flush()

        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        for client in fetched_plans:
            client.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.stdout.write('\nTest 8: Passed ✅\n')
        self.stdout.flush()

    def _test_import_csv(self):
        self.stdout.write('\nTest 9: Importing plans from csv\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/plans_export.csv'
        Plan.import_plans(path, '.csv', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.stdout.write('Test 9: Passed ✅\n')
        self.stdout.flush()

    def _test_import_xlsx(self):
        self.stdout.write('\nTest 10: Importing plans from xlsx\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/plans_export.xlsx'
        Plan.import_plans(path, '.xlsx', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.stdout.write('Test 10: Passed ✅\n')
        self.stdout.flush()

    def _test_import_pdf(self):
        self.stdout.write('\nTest 11: Importing plans from pdf\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests/plans_export.pdf'
        Plan.import_plans(path, '.pdf', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.stdout.write('Test 11: Passed ✅\n')
        self.stdout.flush()
 

class TestSubscription(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.stdout.write(f'\nStarting subscription test...')
        cls.stdout.flush()

        cls._test_setup(cls)
        cls._test_create_subscription(cls)
        cls._test_update_subscription(cls)
        cls._test_delete_subscription(cls)
        cls._test_export_csv(cls)
        cls._test_export_xlsx(cls)
        cls._test_export_pdf(cls)
        cls._test_assigned_users(cls)

    def _test_setup(self):
        self.stdout.write('\nSetting up db with users, plan and payment\n')
        self.stdout.flush()

        for client in get_client():
            new_client = Client(**client)
            new_client.get_id()
            new_client.save_to_db()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.get_id()
            new_plan.save_to_db()

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        self.stdout.write('Setup complete ✅\n')
        self.stdout.flush()

    def _test_create_subscription(self):
        self.stdout.write('\nTest 1: Creating Subscription from test data\n')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()
        client = fetched_clients[0]

        fetched_plans = Plan.fetch_all()
        plan = fetched_plans[0]
        # fetched_payments = Payment.fetch_all()
        # payment = fetched_payments[0]

        sub_obj = {
            'plan_id': plan.plan_id,
            'client_id': client.client_id,
            'plan_unit': 1,
            'discount': 10, # convert from integer
            'discount_type': 'percent',
            'vat': 10, 
            'status': 'booked',
            'payment_status': 'pending'
        }

        sub_obj2 = {
            'plan_id': plan.plan_id,
            'client_id': client.client_id,
            'plan_unit': 2,
            'discount': 10, # convert from integer
            'discount_type': 'percent',
            'vat': 10, 
            'status': 'booked',
            'payment_status': 'pending'
        }

        new_subscription = Subscription(**sub_obj)
        new_subscription.get_id()
        new_subscription.save_to_db()

        second_subscription = Subscription(**sub_obj2)
        second_subscription.get_id()
        second_subscription.save_to_db()

        
        refetch_subscription = Subscription.fetch_one(new_subscription.subscription_id)
        assert new_subscription.subscription_id == refetch_subscription.subscription_id

        self.stdout.write('\nTest 1: Passed ✅')
        self.stdout.flush()

    def _test_update_subscription(self):
        self.stdout.write('\nTest 2: Updating subscriptions in DB')
        self.stdout.flush()

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]
        
        one_subscription.status = 'running'

        one_subscription.update()
    
        one_subscription_refetched = Subscription.fetch_one(one_subscription.subscription_id)

        assert one_subscription_refetched.status == one_subscription.status

        self.stdout.write('\nTest 2: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_subscription(self):
        self.stdout.write('\nTest 3: Delete Subscription in DB\n')
        self.stdout.flush()

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.delete()
    
        one_subscription_refetched = Subscription.fetch_one(one_subscription.subscription_id)

        assert one_subscription_refetched is None

        self.stdout.write('\nTest 3: Passed ✅')
        self.stdout.flush()

    def _test_export_csv(self):
        self.stdout.write('\nTest 4: Export Subscription to csv\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_subscription('.csv', path)
        assert os.path.isfile(path / 'subscription_export.csv')
        self.stdout.write('\nTest 4: Passed ✅')
        self.stdout.flush()

    def _test_export_xlsx(self):
        self.stdout.write('\nTest 5: Export Subscription to xlsx\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_subscription('.xlsx', path)
        assert os.path.isfile(path / 'subscription_export.xlsx')
        self.stdout.write('\nTest 5: Passed ✅')
        self.stdout.flush()

    def _test_export_pdf(self):
        self.stdout.write('\nTest 6: Export Subscription to pdf\n')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_subscription('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/subscription_export.pdf')
        self.stdout.write('\nTest 6: Passed ✅')
        self.stdout.flush()

    def _test_assigned_users(self):
        self.stdout.write('\nTest 7: Assign a user to subscription')
        self.stdout.flush()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.set_assigned_client(one_client)

        assert len(one_subscription.assigned_users) > 0
        assert one_subscription.assigned_users[0].client_id == one_client.client_id

        assigned_user = AssignedClient.get_user(one_subscription.subscription_id, one_client.client_id)

        assert assigned_user[0][0] == one_subscription.assigned_users[0].client_id

        self.stdout.write('\nTest 7: Passed ✅\n')
        self.stdout.flush()


class TestPayment(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.stdout.write(f'\nStarting payment test...\n')
        cls.stdout.flush()

        cls._test_create_payments(cls)
        cls._test_fetch_payments(cls)
        cls._test_update_payment(cls)
        cls._test_delete_payment(cls)

    def _test_create_payments(self):
        self.stdout.write('\nTest 1: Creating payments from test data\n')
        self.stdout.flush()

        client_data = {
            'first_name': 'Client',
            'last_name': 'One',
            'company_name': 'One Company',
            'email': 'clientone@mail.com',
            'phone': '081000000001',
            'display_name': 'client'
        }

        plan_data = {
            'plan_name': '1 Slot',
            'duration': 1,
            'plan_type': 'daily',
            'slot': 1,
            'guest_pass': 0,
            'price': 6000
        }

        client = Client(**client_data)
        client.get_id()
        client.save_to_db()

        # check if client exist in db
        client = Client.fetch_one(client_data['phone'], by_phone=True)
        assert client is not None

        plan = Plan(**plan_data)
        plan.get_id()
        plan.save_to_db()

        # check if plan exist in db
        plan = Plan.fetch_one(plan_data['plan_name'], by_name=True)
        assert plan is not None

        sub_obj = {
            'plan_id': plan.plan_id,
            'client_id': client.client_id,
            'plan_unit': 3,
            'discount': 10, # convert from integer
            'discount_type': 'percent',
            'vat': 10, 
            'status': 'booked',
            'payment_status': 'pending'
        }

        sub = Subscription(**sub_obj)
        sub.get_id()
        sub.save_to_db()

        for i in range(1,4):
            payment_data = {
                'amount': 1000 * i,
                'client_id': client.client_id,
                'subscription_id': sub.subscription_id
            }
            
            # get subscription from test
            new_payment = Payment(**payment_data)
            new_payment.get_id()
            new_payment.save_to_db()
            # break

            # time.sleep(5)

        self.stdout.write('\nTest 1: Passed ✅\n')
        self.stdout.flush()

    def _test_fetch_payments(self):
        self.stdout.write('\nTest 2: Fetching payments from DB\n')
        self.stdout.flush()

        fetched_payments = Payment.fetch_all()
        assert len(fetched_payments) > 0

        one_payment = Payment.fetch_one(fetched_payments[1].payment_id)
        assert one_payment.amount == fetched_payments[1].amount

        filter_by_amount = Payment.filter_payments((1000, 7000), by_amount=True)
        assert len(filter_by_amount) > 0

        filter_by_date = Payment.filter_payments(self.current_year, by_date=True)
        assert len(filter_by_date) > 0

        self.stdout.write('\nTest 2: Passed ✅\n')
        self.stdout.flush()

    def _test_update_payment(self):
        self.stdout.write('\nTest 3: Updating payment in DB\n')
        self.stdout.flush()

        fetched_payment = Payment.fetch_all()

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]
        
        one_payment.amount = 10

        one_payment.update()
    
        one_payment_refetched = Payment.fetch_one(one_payment.payment_id)

        assert one_payment_refetched.amount == one_payment.amount

        self.stdout.write('\nTest 3: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_payment(self):
        self.stdout.write('\nTest 4: Delete payment in DB\n')
        self.stdout.flush()

        fetched_payment = Payment.fetch_all()

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]

        one_payment.delete()
    
        fetched_payment_again = Payment.fetch_all()

        assert len(fetched_payment) != len(fetched_payment_again)

        self.stdout.write('\nTest 4: Passed ✅\n')
        self.stdout.flush()


class TestVisit(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.stdout.write(f'\nStarting visits test...\n')
        cls.stdout.flush()

        cls._test_setup(cls)
        cls._test_create_visit(cls)
        # cls._test_delete_visit(cls)
        cls._test_export_pdf(cls)

    def _test_setup(self):
        self.stdout.write('Setting up db with users, plan, and subscription\n')
        self.stdout.flush()

        for client in get_client():
            new_client = Client(**client)
            new_client.get_id()
            new_client.save_to_db()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.get_id()
            new_plan.save_to_db()

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        client = fetched_clients[0]
        plan = fetched_plans[0]

        sub_obj = {
            'plan_id': plan.plan_id,
            'client_id': client.client_id,
            'plan_unit': 3,
            'discount': 10, # convert from integer
            'discount_type': 'percent',
            'vat': 10, 
            'status': 'booked',
            'payment_status': 'pending'
        }

        new_subscription = Subscription(**sub_obj)
        new_subscription.get_id()
        new_subscription.save_to_db()

        fetched_subscriptions = Subscription.fetch_all()

        one_subscription = fetched_subscriptions[0]
        one_subscription.set_assigned_client(client)

        self.sub_id = one_subscription.subscription_id

        assert len(one_subscription.assigned_users) > 0

        self.stdout.write('Setup complete ✅\n')
        self.stdout.flush()

    def _test_create_visit(self):
        self.stdout.write('\nTest 1: Creating Visit from subscription data\n')
        self.stdout.flush()

        fetched_subscription = Subscription.fetch_one(self.sub_id)

        assert fetched_subscription is not None

        fetched_subscription.log_client_to_visit(fetched_subscription.client)

        visits = Visit.get_client_visits_per_sub(fetched_subscription.subscription_id)

        assert visits[0][0] == fetched_subscription.client.first_name
        assert visits[0][1] == fetched_subscription.client.last_name
        assert visits[0][2] == fetched_subscription.client.company_name

        self.stdout.write('\nTest 1: Passed ✅\n')
        self.stdout.flush()

    def _test_delete_visit(self):
        self.stdout.write('\nTest 3: Delete Subscription in DB')
        self.stdout.flush()

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.delete()
    
        one_subscription_refetched = Subscription.fetch_one(one_subscription.subscription_id)

        assert one_subscription_refetched is None

        self.stdout.write('\nTest 3: Passed ✅\n')
        self.stdout.flush()

    def _test_export_pdf(self):
        self.stdout.write('\nTest 2: Export Visits to pdf')
        self.stdout.flush()
        path = app_config.BASE_DIR / 'tests'

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        Visit.export_visits(path, sub_id=one_subscription.subscription_id)
        
        assert os.path.isfile(app_config.BASE_DIR / 'tests/visits_by_date_export.pdf')
        assert os.path.isfile(app_config.BASE_DIR / 'tests/visits_by_count_export.pdf')
        self.stdout.write('\nTest 2: Passed ✅\n')
        self.stdout.flush()

