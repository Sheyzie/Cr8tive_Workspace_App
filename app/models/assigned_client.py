import time
import inspect
from typing import Self
from database.db import InitDB
from exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from notification.notification import Notification
from helpers.db_helpers import insert_to_db
import logging


logger = logging.getLogger(__name__)


class AssignedClient(InitDB):
    def __init__(self, using: str=None, **kwargs):
        super().__init__(using=using)
        self.subscription_id: str = None
        self.client_id: str = None
        self. created_at: str = None
        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def _get_from_kwargs(self, **kwargs) -> None:
        subscription_id = kwargs.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id
            
        client_id = kwargs.get('client_id')
        if client_id:
            self.client_id = client_id

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self) -> None:
        if not self.subscription_id:
            raise ValidationError('Subscription ID is required')
        if not self.client_id:
            raise ValidationError('Client ID is required')
        if not self.created_at:
            raise ValidationError('Created at field  is required')

    @classmethod    
    def save_to_db(cls, sub_id: str, client_id: str) -> None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        try:
            values = (sub_id, client_id, created_at)
            insert_to_db('assigned_client', cursor, values)
            conn.commit()
            conn.close()
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)

    @classmethod
    def delete_user(cls, sub_id: str, client_id: str) -> None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        
        query = '''
            DELETE FROM assigned_client WHERE subscription_id = ? AND client_id =?;
        '''

        try:
            cursor.execute(query, (sub_id, client_id))
            conn.commit()
            conn.close()
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)

    @classmethod
    def get_user(cls, sub_id, client_id, using=None) -> Self | None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
    
        try:
            query = '''
                SELECT client_id FROM assigned_client WHERE subscription_id = ? AND client_id = ?;
            '''

            cursor.execute(query, (sub_id,client_id))
            assigned_client = cursor.fetchall()

            return assigned_client
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, sub_id: str, using: str=None) -> list:
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
        conn = cls._connect_to_db(cls)
    
        try:
            cursor = conn.cursor()
            query = '''
                SELECT client_id FROM assigned_client WHERE subscription_id = ?;
            '''

            cursor.execute(query, (sub_id,))

            assigned_clients = cursor.fetchall()

            return assigned_clients
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return None


