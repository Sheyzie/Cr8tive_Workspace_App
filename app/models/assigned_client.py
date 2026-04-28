import time
import inspect
from typing import Self
from database.db import InitDB
from database.tables import TABLES_MAP
from exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from notification.notification import Notification
from helpers.db_helpers import insert_to_db
import logging


logger = logging.getLogger(__name__)


class AssignedClient(InitDB):
    '''
    AssignedClient model for the assigned_client table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }

    '''
    model_name = 'assigned_client'

    def __init__(self,  **kwargs):
        super().__init__()
        self.assigned_client_id = None
        self.subscription_id: str = None
        self.client_id: str = None
        self. created_at: str = None
        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            logger.exception(str(err.message))
            self.write_error(str(err.message))
            raise err

    def _reset_fields(self):
        self.assigned_client_id = None
        self.subscription_id = None
        self.client_id = None
        self. created_at = None

    def _get_from_kwargs(self, **kwargs) -> None:
        assigned_client_id = kwargs.get('assigned_client_id', 10)
        if assigned_client_id:
            self.assigned_client_id = assigned_client_id

        subscription_id = kwargs.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id
            
        client_id = kwargs.get('client_id')
        if client_id:
            self.client_id = client_id

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)
        
        self._verify_pk()
        if check_id:
            if not self.assigned_client_id:
                raise ValidationError('Assigned client ID not set')
            if not self._verify_pk():
                raise ValidationError('Assigned User ID is not valid')

        if not self.subscription_id:
            raise ValidationError('Subscription ID is required')
        if not self.client_id:
            raise ValidationError('Client ID is required')
        
    @classmethod
    def delete_user(cls, sub_id: str, client_id: str) -> None:
        
        query = '''
            DELETE FROM assigned_client WHERE subscription_id = ? AND client_id =?;
        '''

        cls.custom(query=query, values=(sub_id, client_id))

        user = cls.get_user(sub_id=sub_id, client_id=client_id)

        if user is not None:
            cls.write_error('User not delete from subscription')
            logger.exception('User not delete from subscription')

    @classmethod
    def get_user(cls, sub_id, client_id) -> Self | None:
        '''
        returns the client id if user is assigned to the subscription
        '''
        
        query = '''
            SELECT client_id FROM assigned_client WHERE subscription_id = ? AND client_id = ?;
        '''

        result = cls.custom(query=query, values=(sub_id, client_id), result_only=True)
        
        return result[0]
        

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
            cls.write_error(str(err))
            raise err


