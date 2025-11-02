import time
import inspect
from datetime import datetime, timedelta
from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from helpers.export_helper import export_helper
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)

from .plan import Plan
from .client import Client
from .payment import Payment


class Subscription(InitDB):
    def __init__(self,using: str=None, **kwargs):
        super().__init__(using=using)
        self.subscription_id: str = None
        self.plan = None
        self.client = None
        self.payment = None
        self.plan_unit: int = 0
        self.expiration_date: str = None
        self.status: str = None
        self.created_at: str = None
        self.updated_at: str = None

        self.assigned_users = []

        if kwargs:
            data = kwargs.get('kwargs')
            self._get_from_kwargs(kwargs=data)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def _get_from_kwargs(self, **kwargs):
        data = kwargs.get('kwargs')
        subscription_id = data.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id

        plan = data.get('plan')
        if plan and isinstance(plan, Plan):
            self.plan = plan

        client = data.get('client')
        if client and isinstance(client, Client):
            self.client = client
        
        payment = data.get('payment')
        if payment and isinstance(payment, Payment):
            self.payment = payment

        plan_unit = data.get('plan_unit')
        if plan_unit and isinstance(plan_unit, (int, float)):
            self.plan_unit = plan_unit

        expiration_date = data.get('expiration_date')
        if expiration_date:
            self.expiration_date = expiration_date

        status = data.get('status')
        if status:
            self.status = status

        assigned_users = data.get('assigned_users')
        if assigned_users:
            self.assigned_users = assigned_users

        created_at = data.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = data.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False):
        STATUS_TYPE = ['booked', 'running', 'expired']
        if not self.plan:
            raise ValidationError('Plan is required')
        if not self.client:
            raise ValidationError('Client is required')
        if not self.payment:
            raise ValidationError('Payment is required')
        if not self.plan_unit > 0:
            raise ValidationError('Plan unit can not be less than 1')
        if not self.status or self.status not in STATUS_TYPE:
            raise ValidationError(f'Status is required and must include {STATUS_TYPE}')
        
        if check_id:
            if not self.subscription_id:
                raise ValidationError('Subscription ID is required')
            if not self.expiration_date:
                raise ValidationError('Expiration Date is required')
        
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('subscription', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Subscription ID')
            
            self.subscription_id = id_string
            
            log_to_file('Subscription', 'Success', f'Subscription ID generated')
            
            cursor.close()
            self.conn.close()

    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.plan.plan_id, self.client.client_id, self.payment.payment_id, self.plan_unit, self.expiration_date, self.status, updated_at, self.subscription_id)
                    update_in_db('subscription', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                self._set_expiration()
                values = (self.subscription_id, self.plan.plan_id, self.client.client_id, self.payment.payment_id, self.plan_unit, self.expiration_date, self.status, created_at, updated_at)
                insert_to_db('subscription', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                log_error_to_file('Subscription', 'Error', f"Error saving subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                log_error_to_file('Subscription', 'Error', f'{err}')
                log_to_file('Subscription', 'Error', f"Error saving subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                Notification.send_notification(err)

    def _set_expiration(self):
        match(self.plan.plan_type):
            case 'hourly':
                expiration_date = datetime.now() + timedelta(hours=(self.plan.duration * self.plan_unit))
                
            case 'daily':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit))
            case 'weekly':
                expiration_date = datetime.now() + timedelta(weeks=(self.plan.duration * self.plan_unit))
            case 'monthly':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 30))
            case 'half-year':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 183))
            case 'yearly':
                expiration_date = datetime.now() + timedelta(days=(self.plan.duration * self.plan_unit * 365))
        self.expiration_date = expiration_date.strftime('%Y-%m-%d %H:%M:%S')

    def update(self):
        self._validate(check_id=True)
        self.save_to_db(update=True)

    def delete(self):
        self._validate(check_id=True)
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            self.query = '''
                DELETE FROM subscription WHERE subscription_id = ?;
            '''

            try:
                cursor.execute(self.query, (self.subscription_id,))
                self.conn.commit()
                self.conn.close()
            except Exception as err:
                log_error_to_file('Subscription', 'Error', f"Error deleting subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                log_error_to_file('Subscription', 'Error', f'{err}')
                log_to_file('Subscription', 'Error', f"Error deleting subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                Notification.send_notification(err)

    @classmethod
    def fetch_one(cls, sub_id, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
    
        try:
            sub_data = fetch_one_entry('subscription', cursor, sub_id)
            
            if sub_data is None:
                return None
            
            if sub_data:
                # get other datas
                plan_id = sub_data[1]
                plan = Plan.fetch_one(plan_id, using=using)

                client_id = sub_data[2]
                client = Client.fetch_one(client_id, using=using)

                payment_id = sub_data[3]
                payment = Payment.fetch_one(payment_id, using=using)

                # screat subscription data obj
                sub_data_obj = {
                    'subscription_id': sub_data[0],
                    'plan': plan,
                    'client': client,
                    'payment': payment,
                    'plan_unit': sub_data[4],
                    'expiration_date': sub_data[5],
                    'status': sub_data[6],
                    'created_at': sub_data[7],
                    'updated_at': sub_data[8],
                }

                subscription = Subscription(kwargs=sub_data_obj, using=using)
                return subscription
            else:
                return None
        except Exception as err:
            log_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls, col_names=False, using: str=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        subscriptions = []

        try:
            # will return tuple(subscriptions, column name) if col_names is True
            subscriptions_data = fetch_all_entry('subscription', cursor, col_names=col_names)

            if not len(subscriptions_data) > 0:
                return []
            
            # unpack data if column_names is True
            if col_names:
                subscriptions_data, column_names = subscriptions_data

            for subscription_data in subscriptions_data:
                # get other datas
                plan_id = subscription_data[1]
                plan = Plan.fetch_one(plan_id, using=using)

                client_id = subscription_data[2]
                client = Client.fetch_one(client_id, using=using)

                payment_id = subscription_data[3]
                payment = Payment.fetch_one(payment_id, using=using)
                
                # create subscription data obj
                subscription_data_obj = {
                    'subscription_id': subscription_data[0],
                    'plan': plan,
                    'client': client,
                    'payment': payment,
                    'plan_unit': subscription_data[4],
                    'expiration_date': subscription_data[5],
                    'status': subscription_data[6],
                    'created_at': subscription_data[7],
                    'updated_at': subscription_data[8],
                }

                subscription = Subscription(kwargs=subscription_data_obj, using=using)
                subscriptions.append(subscription)

            # return (subscriptions, column_names) for export
            if col_names:                
                return (subscriptions, column_names) if subscriptions else []
            
            return subscriptions
        except Exception as err:
            log_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, value, by_user=False, by_plan=False, by_payment=False, created_at=False, col_names=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        subscriptions = []
        try:
            if conn:
                cursor = conn.cursor()
                if by_user:
                    query = '''
                        SELECT * FROM subscription WHERE client_id = ?;
                    '''
                    cursor.execute(query, (value,))

                if by_plan:
                    query = '''
                        SELECT * FROM subscription WHERE plan_id = ?;
                    '''
                    cursor.execute(query, (value,))

                if by_payment:
                    query = '''
                        SELECT * FROM subscription WHERE payment_id = ?;
                    '''
                    cursor.execute(query, (value,))

                if created_at:
                    query = '''
                        SELECT * FROM subscription WHERE created_at LIKE ?;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                subscriptions_data = cursor.fetchall()

                if not len(subscriptions_data) > 0:
                    return []
                
                
                for subscription_data in subscriptions_data:
                    # get other datas
                    plan_id = subscription_data[1]
                    plan = Plan.fetch_one(plan_id, using=using)

                    client_id = subscription_data[2]
                    client = Client.fetch_one(client_id, using=using)

                    payment_id = subscription_data[3]
                    payment = Payment.fetch_one(payment_id, using=using)

                    # screat subscription data obj
                    subscription_data_obj = {
                        'subscription_id': subscription_data[0],
                        'plan': plan,
                        'client': client,
                        'payment': payment,
                        'plan_unit': subscription_data[4],
                        'expiration_date': subscription_data[5],
                        'status': subscription_data[6],
                        'created_at': subscription_data[7],
                        'updated_at': subscription_data[8],
                    }

                    subscription = Subscription(kwargs=subscription_data_obj, using=using)
                    subscriptions.append(subscription)
                
                if col_names:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    
                    return (subscriptions, column_names) if subscriptions else []
                
                return subscriptions
        except Exception as err:
            log_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f"Error fetching subscription @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod
    def export_subscription(cls, file_type, path, value=None, by_user=False, by_month=False, by_year=False, using: str=None):
        if not value:
            subscriptions, column_names = Subscription.fetch_all(col_names=True, using=using)
    
        if by_user:
            subscriptions, column_names = Subscription.filter_sub(value, by_user=True, col_names=True, using=using)

        if by_month or by_year:
            subscriptions, column_names = Subscription.filter_sub(value, created_at=True, col_names=True, using=using)

        column_names = column_names if column_names else None

        # remove unnecessary data like subcription_id
        formated_subscriptions = []
        total_count = 0
        total_price = 0
        total_amount_paid = 0
        processed_payment = set()
        for subscription in subscriptions:
            # subscription = list(subscription)
            # subscription.pop(0)
            # subscription.pop(-1)
            total_count += 1
            total_price += subscription.payment.total_price
            total_amount_paid += subscription.payment.amount_paid
            formated_subscriptions.append([
                subscription.created_at,
                f'{subscription.client.first_name} {subscription.client.last_name}' if subscription.client.first_name else subscription.client.company_name,
                subscription.plan.plan_name,
                subscription.plan.price,
                subscription.payment.amount_paid if subscription.payment.payment_id not in processed_payment else 0,
                subscription.payment.discount,
                subscription.payment.tax,
                subscription.expiration_date,
                subscription.status
            ])

            processed_payment.add(subscription.payment.payment_id)

        # add totals to data
        formated_subscriptions.append([
            'TOTAL',
            total_count,
            total_count,
            total_price,
            total_amount_paid,
            '-',
            '-',
            '-',
            '-'
        ])
        
        formated_column_name = [
            'DATE',
            'CLIENT',
            'PLAN',
            'PRICE',
            'AMOUNT PAID',
            'DISCOUNT',
            'TAX',
            'VALIDITY',
            'STATUS'
        ]

        data = {
            'entries': formated_subscriptions,
            'headers': formated_column_name
        }

        export_helper(cls, file_type, path, data=data, name='subscription_export', using=using)
        print('Export complete')

