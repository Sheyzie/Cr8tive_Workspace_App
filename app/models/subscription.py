import uuid
from pathlib import Path
import time

from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)


class Subscription(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.subscription_id = None
        self.plan_id = None
        self.client_id = None
        self.payment_id = None
        self.expiration = None
        self.status = None
        self.created_at = None
        self.updated_at = None
        if kwargs:
            self._get_from_kwargs(kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)


    def _get_from_kwargs(self, **kwargs):
        subscription_id = kwargs.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id

        plan_id = kwargs.get('plan_id')
        if plan_id:
            self.plan_id = plan_id

        client_id = kwargs.get('client_id')
        if client_id:
            self.client_id = client_id
        
        payment_id = kwargs.get('payment_id')
        if payment_id:
            self.payment_id = payment_id

        expiration = kwargs.get('expiration')
        if expiration:
            self.expiration = expiration

        status = kwargs.get('status')
        if status:
            self.status = status

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False):
        if not self.plan_id:
            raise ValidationError('Plan ID is required')
        if not self.client_id:
            raise ValidationError('Client ID is required')
        if not self.payment_id:
            raise ValidationError('Payment ID is required')
        if not self.expiration:
            raise ValidationError('Expiration is required')
        if self.status:
            raise ValidationError('Status is required')
        
        if check_id:
            if not self.subscription_id:
                raise ValidationError('Subscription ID is required')
        
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
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
            cursor = self.conn.cursor(dictionary=True)
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.plan_id, self.client_id, self.expiration, self.status, updated_at, self.subscription_id)
                    update_in_db('subscription', cursor, values)
                    return

                values = (self.subscription_id, self.plan_id, self.client_id, self.payment_id, self.expiration, self.status, self.created_at, self.updated_at)
                insert_to_db('subscription', cursor, values)
            except ValueError as err:
                log_error_to_file('Subscription', 'Error', f'Error saving subscription')
                log_error_to_file('Subscription', 'Error', f'{err}')
                log_to_file('Subscription', 'Error', f'Error saving subscription')
                Notification.send_notification(err)
            
    @classmethod
    def fetch_one(cls, sub_id):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        # TODO: Implement a join statement to retrieve plan and client
        try:
            sub_data = fetch_one_entry('subscription', cursor, sub_id)

            if sub_data:
                subscription = Subscription(**sub_data)
                return subscription
            else:
                return None
        except Exception as err:
            log_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls, col_names):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
        try:
            subscriptions = fetch_all_entry('subscription', cursor, col_names=col_names)
            return subscriptions
        except Exception as err:
            log_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, value, by_user=False, by_plan=False, by_payment=False, created_at=False):
        conn = cls._connect_to_db()
        try:
            if conn:
                cursor = conn.cursor(dictionary=True)
                if by_user:
                    query = '''
                        SELECT * FROM subscription WHERE user_id = %s;
                    '''
                    cursor.execute(query, (value,))

                if by_plan:
                    query = '''
                        SELECT * FROM subscription WHERE plan_id = %s;
                    '''
                    cursor.execute(query, (value,))

                if by_payment:
                    query = '''
                        SELECT * FROM subscription WHERE payment_id = %s;
                    '''
                    cursor.execute(query, (value,))

                if created_at:
                    query = '''
                        SELECT * FROM subscription WHERE created_at LIKE %s;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                clients = cursor.fetchall()

                return clients
        except Exception as err:
            log_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'Error getting subscription from db')
            log_error_to_file('Subscription', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod
    def export_subscription(cls, file_type, path):
        export_helper(cls, file_type, path, 'subscription_export')
        print('Export complete')

