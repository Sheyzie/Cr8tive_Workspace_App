import time
import inspect
from database.db import InitDB
from exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)


class AssignedClient(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.subscription_id = None
        self.client_id = None
        self. created_at = None
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
            
        client_id = kwargs.get('client_id')
        if client_id:
            self.client_id = client_id


        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False):
        if not self.subscription_id:
            raise ValidationError('Subscription ID is required')
        if not self.client_id:
            raise ValidationError('Client ID is required')
        if not self.created_at:
            raise ValidationError('Created at field  is required')
        
    def save_to_db(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                values = (self.subscription_id, self.client_id, created_at)
                insert_to_db('assigned_client', cursor, values)
            except ValueError as err:
                log_error_to_file('Assigned_client', 'Error', f'Error saving assigned_client')
                log_error_to_file('Assigned_client', 'Error', f'{err}')
                log_to_file('Assigned_client', 'Error', f'Error saving assigned_client')
                Notification.send_notification(err)
            
    @classmethod
    def get_user(cls, sub_id, client_id):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
    
        try:
            query = '''
                SELECT client_id FROM assigned_client WHERE subscription_id = %s AND client_id = %s
            '''

            assigned_client = cursor.execute(query, (sub_id,client_id))

            return assigned_client
        except Exception as err:
            log_to_file('Assigned_client', 'Error', f'Error getting assigned_client from db')
            log_error_to_file('Assigned_client', 'Error', f'Error getting assigned_client from db')
            log_error_to_file('Assigned_client', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, sub_id):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
    
        try:
            query = '''
                SELECT client_id FROM assigned_client WHERE subscription_id = %s
            '''

            assigned_clients = cursor.execute(query, (sub_id,))

            return assigned_clients
        except Exception as err:
            log_to_file('Assigned_client', 'Error', f'Error getting assigned_client from db')
            log_error_to_file('Assigned_client', 'Error', f'Error getting assigned_client from db')
            log_error_to_file('Assigned_client', 'Error', f'{err}')
            Notification.send_notification(err)
            return None


