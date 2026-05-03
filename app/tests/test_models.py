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

    @classmethod
    def write(self, text):
        self.stdout.write(f'\n{text}\n')
        self.stdout.flush()
        
    

class TestClient(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.write('Starting client test...')
        
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
        self.write('Test 1: Creating clients from test data')

        for client in get_client():
            new_client = Client(**client)
            # new_client.get_id()
            new_client.save()
            # time.sleep(5)

        self.write('\nTest 1: Passed ✅\n')
        
    def _test_fetch_client(self):
        self.write('Test 2: Fetching clients from DB')
        

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        one_client = Client.fetch_one(client_id=fetched_clients[1].client_id)
        assert one_client.first_name == fetched_clients[1].first_name

        filter_by_name = Client.filter(first_name='Client')
        assert len(filter_by_name) > 0

        
        filter_by_date = Client.filter(created_at=self.current_year)
        assert len(filter_by_date) > 0

        self.write('\nTest 2: Passed ✅\n')
        
    def _test_update_client(self):
        self.write('Test 3: Updating clients in DB')

        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]
        
        one_client.first_name = 'Updated Client'

        one_client.update()
    
        one_client_refetched = Client.fetch_one(client_id=one_client.client_id)

        assert one_client_refetched.first_name == one_client.first_name

        self.write('\nTest 3: Passed ✅\n')
        
    def _test_delete_client(self):
        self.write('Test 4: Delete clients in DB')
        
        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        one_client.delete()
    
        one_client_refetched = Client.fetch_one(client_id=one_client.client_id)

        assert one_client_refetched is None

        self.write('\nTest 4: Passed ✅\n')
        
    def _test_export_csv(self):
        self.write('Test 5: Export clients to csv')
        
        path = app_config.BASE_DIR / 'tests'
        Client.export_model('.csv', path)
        assert os.path.isfile(path / 'clients_export.csv')
        self.write('\nTest 5: Passed ✅\n')
        
    def _test_export_xlsx(self):
        self.write('Test 6: Export clients to xlsx')
        
        path = app_config.BASE_DIR / 'tests'
        Client.export_model('.xlsx', path)
        assert os.path.isfile(path / 'clients_export.xlsx')
        self.write('\nTest 6: Passed ✅\n')
        
    def _test_export_pdf(self):
        self.write('Test 7: Export clients to pdf')

        path = app_config.BASE_DIR / 'tests'
        Client.export_model('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/clients_export.pdf')
        self.write('\nTest 7: Passed ✅\n')
        
    def _test_delete_all_clients(self):
        self.write('Test 8: Delete all clients in DB')
        
        fetched_clients = Client.fetch_all()

        assert len(fetched_clients) > 0

        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.write('\nTest 8: Passed ✅\n')
        
    def _test_import_csv(self):
        self.write('Test 9: Importing clients from csv')
        
        path = app_config.BASE_DIR / 'tests/clients_export.csv'
        Client.import_model(path, '.csv', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.write('\nTest 9: Passed ✅\n')
        
    def _test_import_xlsx(self):
        self.write('Test 10: Importing clients from xlsx')
        
        path = app_config.BASE_DIR / 'tests/clients_export.xlsx'
        Client.import_model(path, '.xlsx', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        
        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.write('\nTest 10: Passed ✅\n')
        
    def _test_import_pdf(self):
        self.write('Test 11: Importing clients from pdf')
        
        path = app_config.BASE_DIR / 'tests/clients_export.pdf'
        Client.import_model(path, '.pdf', has_header=True)

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        for client in fetched_clients:
            client.delete()

        refetched_clients = Client.fetch_all()

        assert len(refetched_clients) == 0

        self.write('\nTest 11: Passed ✅\n')
        
 
class TestPlan(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.write(f'Starting plan test..')

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
        self.write('Test 1: Creating plans from test data')
        
        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.save()
            # time.sleep(5)

        self.write('\nTest 1: Passed ✅\n')
        
    def _test_fetch_plans(self):
        self.write('Test 2: Fetching plans from DB')
        

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        one_plan = Plan.fetch_one(plan_id=fetched_plans[1].plan_id)
        assert one_plan.plan_name == fetched_plans[1].plan_name
        assert one_plan.duration == fetched_plans[1].duration
        assert one_plan.price == fetched_plans[1].price

        filter_by_name = Plan.filter(plan_type='daily')
        assert len(filter_by_name) > 0

        filter_by_date = Plan.filter(created_at=self.current_year)
        assert len(filter_by_date) > 0

        self.write('\nTest 2: Passed ✅\n')

    def _test_update_plan(self):
        self.write('Test 3: Updating plans in DB')
        

        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]
        
        one_plan.plan_name = 'Updated 1 Slot'

        one_plan.update()
    
        one_plan_refetched = Plan.fetch_one(plan_id=one_plan.plan_id)

        assert one_plan_refetched.plan_name == one_plan.plan_name

        self.write('\nTest 3: Passed ✅\n')
        
    def _test_delete_plan(self):
        self.write('Test 4: Delete plans in DB')
        

        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        one_plan = fetched_plans[0]

        one_plan.delete()
    
        one_plan_refetched = Plan.fetch_one(plan_id=one_plan.plan_id)

        assert one_plan_refetched is None

        self.write('\nTest 4: Passed ✅\n')
        
    def _test_export_csv(self):
        self.write('Test 5: Export plans to csv')
        
        path = app_config.BASE_DIR / 'tests'
        Plan.export_model('.csv', path)
        assert os.path.isfile(path / 'plans_export.csv')
        self.write('\nTest 5: Passed ✅\n')
        
    def _test_export_xlsx(self):
        self.write('Test 6: Export plans to xlsx')
        
        path = app_config.BASE_DIR / 'tests'
        Plan.export_model('.xlsx', path)
        assert os.path.isfile(path / 'plans_export.xlsx')
        self.write('\nTest 6: Passed ✅\n')
        
    def _test_export_pdf(self):
        self.write('Test 7: Export plans to pdf')
        
        path = app_config.BASE_DIR / 'tests'
        Plan.export_model('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/plans_export.pdf')
        self.write('\nTest 7: Passed ✅\n')
        
    def _test_delete_all_plans(self):
        self.write('Test 8: Delete all plans in DB')
        
        fetched_plans = Plan.fetch_all()

        assert len(fetched_plans) > 0

        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.write('\nTest 8: Passed ✅\n')
        
    def _test_import_csv(self):
        self.write('Test 9: Importing plans from csv')
        
        path = app_config.BASE_DIR / 'tests/plans_export.csv'
        Plan.import_model(path, '.csv', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.write('\nTest 9: Passed ✅\n')
        
    def _test_import_xlsx(self):
        self.write('Test 10: Importing plans from xlsx')
        
        path = app_config.BASE_DIR / 'tests/plans_export.xlsx'
        Plan.import_model(path, '.xlsx', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.write('\nTest 10: Passed ✅\n')
        
    def _test_import_pdf(self):
        self.write('Test 11: Importing plans from pdf')
        
        path = app_config.BASE_DIR / 'tests/plans_export.pdf'
        Plan.import_model(path, '.pdf', has_header=True)

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        
        for plan in fetched_plans:
            plan.delete()

        refetched_plans = Plan.fetch_all()

        assert len(refetched_plans) == 0

        self.write('\nTest 11: Passed ✅\n')
        

class TestSubscription(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.write(f'\nStarting subscription test...')

        cls._test_setup(cls)
        cls._test_create_subscription(cls)
        cls._test_update_subscription(cls)
        cls._test_delete_subscription(cls)
        cls._test_export_csv(cls)
        cls._test_export_xlsx(cls)
        cls._test_export_pdf(cls)
        cls._test_assigned_users(cls)

    def _test_setup(self):
        self.write('\nSetting up db with users, plan and payment')
        
        for client in get_client():
            new_client = Client(**client)
            new_client.save()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.save()

        fetched_plans = Plan.fetch_all()
        assert len(fetched_plans) > 0

        self.write('Setup complete ✅\n')

    def _test_create_subscription(self):
        self.write('Test 1: Creating Subscription from test data')
        
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
        new_subscription.save()

        second_subscription = Subscription(**sub_obj2)
        second_subscription.save()

        refetch_subscription = Subscription.fetch_one(subscription_id=new_subscription.subscription_id)

        assert new_subscription.subscription_id == refetch_subscription.subscription_id

        self.write('\nTest 1: Passed ✅\n')
        
    def _test_update_subscription(self):
        self.write('Test 2: Updating subscriptions in DB')
        
        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]
        
        one_subscription.status = 'running'

        one_subscription.update()
    
        one_subscription_refetched = Subscription.fetch_one(subscription_id=one_subscription.subscription_id)

        assert one_subscription_refetched.status == one_subscription.status

        self.write('\nTest 2: Passed ✅\n')
        
    def _test_delete_subscription(self):
        self.write('Test 3: Delete Subscription in DB')
        
        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.delete()
    
        one_subscription_refetched = Subscription.fetch_one(subscription_id=one_subscription.subscription_id)

        assert one_subscription_refetched is None

        self.write('\nTest 3: Passed ✅\n')
        
    def _test_export_csv(self):
        self.write('Test 4: Export Subscription to csv')
        
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_model('.csv', path)
        assert os.path.isfile(path / 'subscription_export.csv')
        self.write('\nTest 4: Passed ✅\n')
        
    def _test_export_xlsx(self):
        self.write('Test 5: Export Subscription to xlsx')
        
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_model('.xlsx', path)
        assert os.path.isfile(path / 'subscription_export.xlsx')
        self.write('\nTest 5: Passed ✅\n')
        
    def _test_export_pdf(self):
        self.write('Test 6: Export Subscription to pdf')
        
        path = app_config.BASE_DIR / 'tests'
        Subscription.export_model('.pdf', path)
        assert os.path.isfile(app_config.BASE_DIR / 'tests/subscription_export.pdf')
        self.write('\nTest 6: Passed ✅\n')
        
    def _test_assigned_users(self):
        self.write('Test 7: Assign a user to subscription')
        

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        one_client = fetched_clients[0]

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.set_assigned_client(one_client.client_id)

        assert len(one_subscription.assigned_users) > 0
        assert one_subscription.assigned_users[0].client_id == one_client.client_id

        assigned_user = AssignedClient.get_user(one_subscription.subscription_id, one_client.client_id)

        assert assigned_user == one_subscription.assigned_users[0].client_id

        self.write('\nTest 7: Passed ✅\n')
        

class TestPayment(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.write(f'Starting payment test...')

        cls._test_create_payments(cls)
        cls._test_fetch_payments(cls)
        cls._test_update_payment(cls)
        cls._test_delete_payment(cls)

    def _test_create_payments(self):
        self.write('Test 1: Creating payments from test data') 

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
        client.save()

        # check if client exist in db
        client = Client.fetch_one(phone=client_data['phone'])
        assert client is not None

        plan = Plan(**plan_data)
        plan.save()

        # check if plan exist in db
        plan = Plan.fetch_one(plan_name=plan_data['plan_name'])
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
        sub.save()

        for i in range(1,4):
            payment_data = {
                'amount': 1000 * i,
                'client_id': client.client_id,
                'subscription_id': sub.subscription_id
            }
            
            # get subscription from test
            new_payment = Payment(**payment_data)
            new_payment.save()
            # break

            # time.sleep(5)

        self.write('\nTest 1: Passed ✅\n')

    def _test_fetch_payments(self):
        self.write('Test 2: Fetching payments from DB') 

        fetched_payments = Payment.fetch_all()
        assert len(fetched_payments) > 0

        one_payment = Payment.fetch_one(payment_id=fetched_payments[1].payment_id)
        assert one_payment.amount == fetched_payments[1].amount


        filter_by_amount = Payment.filter(amount=(one_payment.amount))
        assert len(filter_by_amount) > 0

        filter_by_date = Payment.filter(created_at=self.current_year)
        assert len(filter_by_date) > 0

        self.write('\nTest 2: Passed ✅\n')
        
    def _test_update_payment(self):
        self.write('Test 3: Updating payment in DB')
        
        fetched_payment = Payment.fetch_all()

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]
        
        one_payment.amount = 10

        one_payment.update()
    
        one_payment_refetched = Payment.fetch_one(payment_id=one_payment.payment_id)

        assert one_payment_refetched.amount == one_payment.amount

        self.write('\nTest 3: Passed ✅\n')
        
    def _test_delete_payment(self):
        self.write('Test 4: Delete payment in DB')
        
        fetched_payment = Payment.fetch_all()

        assert len(fetched_payment) > 0

        one_payment = fetched_payment[0]

        one_payment.delete()
    
        fetched_payment_again = Payment.fetch_all()

        assert len(fetched_payment) != len(fetched_payment_again)

        self.write('\nTest 4: Passed ✅\n')
        

class TestVisit(BaseTestClass):

    @classmethod
    def start_test(cls):
        cls.write(f'Starting visits test...')

        cls._test_setup(cls)
        cls._test_create_visit(cls)
        # cls._test_delete_visit(cls)
        cls._test_export_pdf(cls)

    def _test_setup(self):
        self.write('Setting up db with users, plan, and subscription')
        
        for client in get_client():
            new_client = Client(**client)
            new_client.save()

        fetched_clients = Client.fetch_all()
        assert len(fetched_clients) > 0

        for plan in get_plan():
            new_plan = Plan(**plan)
            new_plan.save()

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
        new_subscription.save()

        self.sub_id = new_subscription.subscription_id

        fetched_subscription = Subscription.fetch_one(subscription_id=self.sub_id)
        fetched_subscription.set_assigned_client(client.client_id)

        assert len(fetched_subscription.assigned_users) > 0

        self.write('Setup complete ✅\n')
        
    def _test_create_visit(self):
        self.write('Test 1: Creating Visit from subscription data')
        
        fetched_subscription = Subscription.fetch_one(subscription_id=self.sub_id)
        
        assert fetched_subscription is not None

        fetched_subscription.log_client_to_visit(fetched_subscription.client_id.client_id)
        
        visits = Visit.get_client_visits_per_sub(fetched_subscription.subscription_id, result_only=True)
        
        assert visits[0] == fetched_subscription.client_id.first_name
        assert visits[1] == fetched_subscription.client_id.last_name
        assert visits[2] == fetched_subscription.client_id.company_name

        self.write('\nTest 1: Passed ✅\n')
        
    def _test_delete_visit(self):
        self.write('Test 3: Delete Subscription in DB')
        
        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        one_subscription.remove_user_visit()
    
        one_subscription_refetched = Subscription.fetch_one(subscription_id=one_subscription.subscription_id)

        assert one_subscription_refetched is None

        self.write('\nTest 3: Passed ✅\n')
        
    def _test_export_pdf(self):
        self.write('Test 2: Export Visits to pdf')
        
        path = app_config.BASE_DIR / 'tests'

        fetched_subscriptions = Subscription.fetch_all()

        assert len(fetched_subscriptions) > 0

        one_subscription = fetched_subscriptions[0]

        Visit.export_model(path, sub_id=one_subscription.subscription_id)
        
        assert os.path.isfile(app_config.BASE_DIR / 'tests/visits_by_date_export.pdf')
        assert os.path.isfile(app_config.BASE_DIR / 'tests/visits_by_count_export.pdf')
        self.write('\nTest 2: Passed ✅\n')
        

