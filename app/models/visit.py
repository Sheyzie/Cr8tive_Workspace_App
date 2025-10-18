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
        self.timestamp = None
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

        timestamp = kwargs.get('timestamp')
        if timestamp:
            self.timestamp = timestamp

    def _validate(self, check_id=False):
        if not self.subscription_id:
            raise ValidationError('Subscription ID is required')
        if not self.timestamp:
            raise ValidationError('Timestamp is required')
        
    def save_to_db(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                values = (self.subscription_id, timestamp)
                insert_to_db('subscription', cursor, values)
            except ValueError as err:
                log_error_to_file('Visit', 'Error', f'Error saving visit')
                log_error_to_file('Visit', 'Error', f'{err}')
                log_to_file('Visit', 'Error', f'Error saving visit')
                Notification.send_notification(err)
            
    @classmethod
    def get_visits(cls, sub_id, get_count=False):
        conn = cls._connect_to_db()
        cursor = conn.cursor(dictionary=True)
    
        try:
            query = '''
                SELECT timestamp FROM visit WHERE subscription_id = %s
            '''
            if get_count:
                query = '''
                    SELECT Count(subscription_id) FROM visit WHERE subscription_id = %s
                '''

            visits = cursor.execute(query, (sub_id,))

            return visits
        except Exception as err:
            log_to_file('Visit', 'Error', f'Error getting visit from db')
            log_error_to_file('Visit', 'Error', f'Error getting visit from db')
            log_error_to_file('Visit', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, value):
        conn = cls._connect_to_db()
        try:
            if conn:
                cursor = conn.cursor(dictionary=True)

                query = '''
                    SELECT * FROM visit WHERE timestamp LIKE %s;
                '''
                cursor.execute(query, ('%' + value + '%',))

                clients = cursor.fetchall()

                return clients
        except Exception as err:
            log_to_file('Visit', 'Error', f'Error getting visit from db')
            log_error_to_file('Visit', 'Error', f'Error getting visit from db')
            log_error_to_file('Visit', 'Error', f'{err}')
            Notification.send_notification(err)


