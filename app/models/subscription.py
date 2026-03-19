import time
import inspect
from typing import Self
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

import logging

from .plan import Plan
from .client import Client
from .assigned_client import AssignedClient
from .visit import Visit


logger = logging.getLogger(__name__)


class Subscription(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.subscription_id: str = None
        self.plan: Plan = None
        self.client: Client = None
        self.plan_unit: int = 0
        self.expiration_date: str = None
        self.discount = 0
        self.discount_type = 'percent'
        self.vat = 0
        self.status: str = None
        self.payment_status: str = None
        self.created_at: str = None
        self.updated_at: str = None

        self.assigned_users: list[Client] = []

        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    @property
    def usage(self):
        # {'hourly', 'daily', 'weekly', 'monthly', 'half-year', 'yearly'}
        match self.plan.plan_type:
            case 'hourly':
                return (self.plan.duration / 24) * self.plan_unit
            case 'daily':
                return (self.plan.duration * self.plan_unit) + self.plan.guest_pass
            case 'weekly':
                return ((self.plan.duration * 7) * self.plan_unit) + self.plan.guest_pass
            case 'monthly':
                return ((self.plan.duration * 30) * self.plan_unit) + self.plan.guest_pass
            case 'half-year':
                return ((self.plan.duration * 183) * self.plan_unit) + self.plan.guest_pass
            case 'yearly':
                return ((self.plan.duration * 365) * self.plan_unit) + self.plan.guest_pass
            case _:
                # return daily
                return (self.plan.duration * self.plan_unit) + self.plan.guest_pass
            
    @property
    def subtotal(self):
        return self.plan.price * self.plan_unit
    
    @property
    def discount_amount(self):
        discount =  self.discount
        if self.discount_type == 'percent':
            discount = self.subtotal * (self.discount / 100)
        return discount
    
    @property
    def vat_amount(self):
        return self.subtotal * (self.vat / 100)
    
    @property
    def total_amount(self):
        return float((self.subtotal - self.discount_amount) + self.vat_amount)
    
    @property
    def payments(self):
        from .payment import Payment
        
        payments = Payment.filter_payments(self.subscription_id, by_subscription=True)

        return payments
    
    @property
    def total_paid(self):
        amount = sum(payment.amount for payment in self.payments)
        
        return  amount if amount else 0

    @property
    def balance(self):
        return self.total_amount - self.total_paid
    
    def __str__(self):
        return f'Subscription for {self.plan.plan_name} by {self.client.get_display_name()}'
    
    def _reset_fields(self):
        self.subscription_id: str = None
        self.plan = None
        self.client = None
        self.plan_unit: int = 0
        self.expiration_date: str = None
        self.discount = 0
        self.discount_type = ''
        self.vat = 0
        self.status: str = None
        self.payment_status: str = None
        self.created_at: str = None
        self.updated_at: str = None

    def _get_from_kwargs(self, **kwargs) -> None:
        subscription_id = kwargs.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id

        plan = Plan.fetch_one(kwargs.get('plan_id'))
        if plan:
            self.plan = plan

        client = Client.fetch_one(kwargs.get('client_id'))
        if client:
            self.client = client

        plan_unit = kwargs.get('plan_unit')
        if plan_unit:
            self.plan_unit = plan_unit

        expiration_date = kwargs.get('expiration_date')
        if expiration_date:
            self.expiration_date = expiration_date

        discount = kwargs.get('discount')
        if discount and isinstance(discount, (int, float)):
            self.discount = discount

        discount_type = kwargs.get('discount_type')
        if discount_type and discount_type in {'percent', 'fixed'}:
            self.discount_type = discount_type

        vat = kwargs.get('vat')
        if vat and isinstance(vat, (int, float)):
            self.vat = vat

        status = kwargs.get('status')
        if status:
            self.status = status

        payment_status = kwargs.get('payment_status')
        if payment_status:
            self.payment_status = payment_status

        assigned_users_id = kwargs.get('assigned_users_id', [])
        assigned_users = []
        for client_id in assigned_users_id:
            client = Client.fetch_one(client_id)
            if client:
                assigned_users.append(client)
        if len(assigned_users) > 0:
            self.assigned_users = assigned_users

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False) -> None:
        STATUS_TYPE = ['booked', 'running', 'expired', 'exhausted']
        PAYMENT_STATUS_TYPE = ['pending', 'partial', 'paid', 'free']

        if not self.plan:
            raise ValidationError('Plan is not set on subscription')
        if not isinstance(self.plan, Plan):
            raise ValidationError('Plan is not valid on subscription')
        if not self.client:
            raise ValidationError('Client not set on subscription')
        if not isinstance(self.client, Client):
            raise ValidationError('Client is not valid on subscription')
        if not isinstance(self.plan_unit, (int, float)):
            raise ValidationError('Plan unit need to be a number')
        if not self.plan_unit > 0:
            raise ValidationError('Plan unit can not be less than 1')
        if not self.discount:
            raise ValidationError('Payment discount not set on subscription')
        if self.discount < 0:
            raise ValidationError('Payment discount cannot be less than zero')
        if not isinstance(self.discount, (int, float)):
            raise ValidationError('Payment discount cannot be letters')
        if self.discount_type not in {'percent', 'fixed'}:
            raise ValidationError('Payment discount type choices are [percent, fixed]')
        if not self.vat:
            raise ValidationError('Payment vat is required')
        if self.vat < 0:
            raise ValidationError('Payment vat cannot be less than zero')
        if not isinstance(self.vat, (int, float)):
            raise ValidationError('Payment vat cannot be letters')
        if not self.status or self.status not in STATUS_TYPE:
            raise ValidationError(f'Status is required and must include {STATUS_TYPE}')
        if not self.payment_status or self.payment_status not in PAYMENT_STATUS_TYPE:
            raise ValidationError(f'Payment status is required. choice {PAYMENT_STATUS_TYPE}')
        if len(self.assigned_users) > 0 and not all(isinstance(u, Client) for u in self.assigned_users):
                raise ValidationError('Assigned users need to be a list of valid client')
            
        
        if check_id:
            if not self.subscription_id:
                raise ValidationError('Subscription ID is required')
            if not self.expiration_date:
                raise ValidationError('Expiration Date is required')
            
            if not isinstance(self.assigned_users, list):
                raise ValidationError('Assigned users need to be a list of valid client')
            
            self._check_subscription_id()
                    
    def get_id(self) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('subscription', cursor)
            
            if not id_string:
                logger.warn('ID not generated')
                self.stderr.write('\033[31m' + 'ID not generated'+ '\033[0m\n')
                self.stderr.flush()
            
            self.subscription_id = id_string
            
            cursor.close()
            self.conn.close()
    
    def _check_subscription_id(self):
        '''
        check if id changed
        '''
        subscription = Subscription.fetch_one(self.subscription_id)

        if not subscription:
            raise ValidationError('Invalid ID for subscription')

    def save_to_db(self, update=False) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.plan.plan_id, self.client.client_id, self.plan_unit, self.expiration_date, int(self.discount * 100), self.discount_type, int(self.vat * 100), self.status, self.payment_status, updated_at, self.subscription_id)
                    update_in_db('subscription', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                self._set_expiration()
                values = (self.subscription_id, self.plan.plan_id, self.client.client_id, self.plan_unit, self.expiration_date, int(self.discount * 100), self.discount_type, int(self.vat * 100), self.status, self.payment_status, created_at, updated_at)
                insert_to_db('subscription', cursor, values)
                self.conn.commit()
                self.conn.close()
            except Exception as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()
                Notification.send_notification(err)

    def _set_expiration(self) -> None:
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

    def update(self) -> None:
        try:
            self._validate(check_id=True)
            self.save_to_db(update=True)
        except ValidationError as err:
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def delete(self):
        try:
            self._validate(check_id=True)

            self._connect_to_db()
            if self.conn:
                cursor = self.conn.cursor()
                self.query = '''
                    DELETE FROM subscription WHERE subscription_id = ?;
                '''

            cursor.execute(self.query, (self.subscription_id,))
            self.conn.commit()
            self.conn.close()
        except ValidationError as err:
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)
        
        except Exception as err:
            logging.error('Error deleting client')
            self.stderr.write(str(err.with_traceback()))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def set_assigned_client(self, client: Client) -> None:
        if client not in self.assigned_users:
            AssignedClient.save_to_db(sub_id=self.subscription_id, client_id=client.client_id)
            self.assigned_users.append(client)

    def remove_assigned_client(self, client: Client) -> None:
        if not len(self.assigned_users) > 0:
            return None
        
        if client in self.assigned_users:
            AssignedClient.delete_user(sub_id=self.subscription_id,client_id=client.client_id)
            self.assigned_users.remove(client)

    def is_user(self, client: Client) -> bool:
        if self.client.client_id == client.client_id:
            return True
        
        for user in self.assigned_users:
            if user.client_id == client.client_id:
                return True
        
        return False
    
    def log_client_to_visit(self, user: Client) -> None:
        is_user: bool = self.is_user(user)
        
        if not is_user:
            Notification.send_notification(f'User: {user} is not a listed assigned user for this subscription')
            return
        
        client = Client.fetch_one(user.client_id)
        
        if client is None:
            logger.warn('Users does not exist')
            Notification.send_notification(f'User: {user} does not exist please remove user from assigned user')
            return
        
         # check if user is an assigned user
        if not self.is_user(client):
            logger.warn('User is does not have access to this subcription')
            return 

        # check if subscription is exhausted or expired
        if self.status not in {'booked', 'running'}:
            logger.warn(f'Can not log user in to {self.status} plan')
            return
        
        is_valid = self.check_expiration()
        if not is_valid:
            logger.warn('Subscription has expired')
            self.status = 'expired'
            self.save_to_db(update=True)

            Notification.send_notification(f'User: {user} does not exist please remove user from assigned user')

            return
        
        if self.usage == Visit.get_all_sub_visits_count(self.subscription_id):
            self.status = 'exhausted'
            self.save_to_db(update=True)
            logger.warn('Usage has been exhausted')
            return
        
        # TODO: validate if plan is hourly
        
        visit = Visit(**{'subscription_id': self.subscription_id, 'client_id': user.client_id})
        visit.get_id()
        visit.save_to_db()

        self.status = 'running'
        self.save_to_db(update=True)

    def remove_user_visit(self, user: Client, date_value: str) -> None:
        # date_value is expecting date in YYYY-MM-DD format
        is_user: bool = self.is_user(user)
        
        if not is_user:
            Notification.send_notification(f'User: {user} is not a listed assigned user for this subscription')
            return
        # client = Client.fetch_one(user.client_id, using=self._db)
        # if client is None:
        #     Notification.send_notification(f'User: {user} does not exist please remove user from assigned user')
        #     return
        
        Visit.delete(self.subscription_id, user.client_id, date_value)

    def check_expiration(self):
        from datetime import datetime

        # convert string to datetime
        exp = datetime.strptime(self.expiration_date, "%Y-%m-%d %H:%M:%S")

        # current time
        now = datetime.now()

        return exp > now

    @classmethod
    def fetch_one(cls, sub_id) -> Self | None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
    
        try:
            sub_data = fetch_one_entry('subscription', cursor, sub_id)
            
            if sub_data is None:
                return None
            
            if sub_data:
                assigned_clients_id = AssignedClient.filter_sub(sub_id=sub_data[0])

                assigned_users_id = []
                if len(assigned_clients_id) > 0:
                    for assigned_client_id_tuple in assigned_clients_id:
                        assigned_users_id.append(assigned_client_id_tuple[0])

                # screat subscription data obj
                sub_data_obj = {
                    'subscription_id': sub_data[0],
                    'plan_id': sub_data[1],
                    'client_id': sub_data[2],
                    'plan_unit': sub_data[3],
                    'expiration_date': sub_data[4],
                    'discount': float(sub_data[5] / 100), # convert from integer
                    'discount_type': sub_data[6],
                    'vat': float(sub_data[7]) / 100, # convert from integer
                    'status': sub_data[8],
                    'payment_status': sub_data[9],
                    'created_at': sub_data[10],
                    'updated_at': sub_data[11],
                    'assigned_users_id': assigned_users_id if len(assigned_users_id) > 0 else []
                }

                subscription = Subscription(**sub_data_obj)
                return subscription
            else:
                return None
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls, col_names=False, using: str=None) -> list:
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
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
                assigned_clients_id = AssignedClient.filter_sub(sub_id=subscription_data[0])

                assigned_users_id = []
                if len(assigned_clients_id) > 0:
                    for assigned_client_id_tuple in assigned_clients_id:
                        assigned_users_id.append(assigned_client_id_tuple[0])

                # screat subscription data obj
                subscription_data_obj = {
                    'subscription_id': subscription_data[0],
                    'plan_id': subscription_data[1],
                    'client_id': subscription_data[2],
                    'plan_unit': subscription_data[3],
                    'expiration_date': subscription_data[4],
                    'discount': float(subscription_data[5] / 100), # convert from integer
                    'discount_type': subscription_data[6],
                    'vat': float(subscription_data[7]) / 100, # convert from integer
                    'status': subscription_data[8],
                    'payment_status': subscription_data[9],
                    'created_at': subscription_data[10],
                    'updated_at': subscription_data[11],
                    'assigned_users_id': assigned_users_id if len(assigned_users_id) > 0 else []
                }

                subscription = Subscription(**subscription_data_obj)
                subscriptions.append(subscription)

            # return (subscriptions, column_names) for export
            if col_names:                
                return (subscriptions, column_names) if subscriptions else []
            
            return subscriptions
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    @classmethod  
    def filter_sub(cls, value, by_user=False, by_plan=False, by_payment=False, created_at=False, col_names=False) -> list:
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
                    assigned_clients_id = AssignedClient.filter_sub(sub_id=subscription_data[0])

                    assigned_users_id = []
                    if len(assigned_clients_id) > 0:
                        for assigned_client_id_tuple in assigned_clients_id:
                            assigned_users_id.append(assigned_client_id_tuple[0])

                    # screat subscription data obj
                    subscription_data_obj = {
                   'subscription_id': subscription_data[0],
                    'plan_id': subscription_data[1],
                    'client_id': subscription_data[2],
                    'plan_unit': subscription_data[3],
                    'expiration_date': subscription_data[4],
                    'discount': float(subscription_data[5] / 100), # convert from integer
                    'discount_type': subscription_data[6],
                    'vat': float(subscription_data[7]) / 100, # convert from integer
                    'status': subscription_data[8],
                    'payment_status': subscription_data[9],
                    'created_at': subscription_data[10],
                    'updated_at': subscription_data[11],
                    'assigned_users_id': assigned_users_id if len(assigned_users_id) > 0 else []
                }

                    subscription = Subscription(kwargs=subscription_data_obj)
                    subscriptions.append(subscription)
                
                if col_names:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    
                    return (subscriptions, column_names) if subscriptions else []
                
                return subscriptions
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    @classmethod
    def export_subscription(cls, file_type, path, value=None, by_user=False, by_month=False, by_year=False) -> None:
        if not value:
            subscriptions, column_names = Subscription.fetch_all(col_names=True)
    
        if by_user:
            subscriptions, column_names = Subscription.filter_sub(value, by_user=True, col_names=True)

        if by_month or by_year:
            subscriptions, column_names = Subscription.filter_sub(value, created_at=True, col_names=True)

        column_names = column_names if column_names else None

        # remove unnecessary data like subcription_id
        formated_subscriptions = []
        total_count = 0
        total_price = 0
        total_amount_paid = 0
        total_discount = 0
        total_vat = 0

        for subscription in subscriptions:
            total_count += 1
            total_price += subscription.total_amount
            total_amount_paid += subscription.total_paid
            total_discount += subscription.discount_amount
            total_vat += subscription.vat_amount
            formated_subscriptions.append([
                subscription.created_at,
                subscription.client.get_display_name(),
                subscription.plan.plan_name,
                subscription.total_amount,
                subscription.total_paid,
                subscription.discount_amount,
                subscription.vat_amount,
                subscription.expiration_date,
                subscription.status
            ])

            # processed_payment.add(subscription.payments.payment_id)

        # add totals to data
        formated_subscriptions.append([
            'TOTAL',
            total_count,
            total_count,
            total_price,
            total_amount_paid,
            total_discount,
            total_vat,
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
            'vat',
            'VALIDITY',
            'STATUS'
        ]

        data = {
            'entries': formated_subscriptions,
            'headers': formated_column_name
        }

        export_helper(cls, file_type, path, data=data, name='subscription_export')
        print('Export complete')



