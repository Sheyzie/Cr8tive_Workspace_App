import time
import inspect
from database.db import InitDB
from database.tables import TABLES_MAP
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from notification.notification import Notification
from helpers.db_helpers import insert_to_db

import logging


logger = logging.getLogger(__name__)


class Visit(InitDB):
    # field_map = TABLES_MAP.get('visit').get('fields')

    def __init__(self, **kwargs):
        super().__init__()
        self.visit_id: str = None
        self.subscription: str = None
        self.client: str = None
        self.timestamp: str = None
        if kwargs:
            self._get_from_kwargs(**kwargs)
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.exception(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def __str__(self):
        return f'{self.client.get_display_name()} visited on {self.timestamp}'

    def _reset_fields(self):
        self.subscription: str = None
        self.client: str = None
        self.timestamp: str = None

    def _get_from_kwargs(self, **kwargs) -> None:
        from .client import Client
        from .subscription import Subscription

        visit_id = kwargs.get('visit_id')
        if visit_id:
            self.visit_id = visit_id

        client = Client.fetch_one(client_id=kwargs.get('client_id'))
        
        if client:
            self.client = client

        subscription = Subscription.fetch_one(subscription_id=kwargs.get('subscription_id'))
        if subscription:
            self.subscription = subscription

        timestamp = kwargs.get('timestamp')
        if timestamp:
            self.timestamp = timestamp

    def _validate(self, check_id=False) -> None:
        from .client import Client
        from .subscription import Subscription

        if check_id:
            if not self.visit_id:
                raise ValidationError('Visit ID not set')
            if not self._verify_pk():
                raise ValidationError('Visit ID is not valid')
            if not self.timestamp:
                raise ValidationError('Timestamp not set on visit')

        if not self.client:
            raise ValidationError('Client not set on visit')
        if not isinstance(self.client, Client):
            raise ValidationError('Client is not valid on visit')
        if not self.subscription: 
            raise ValidationError('Subscription not set on visit')
        if not isinstance(self.subscription, Subscription):
            raise ValidationError('Subscription is not valid on visit')
  
    @classmethod
    def get_client_visits_per_sub(cls, sub_id: str, get_count: bool=False, col_names=False, result_only=False) -> list:
        query = '''
                SELECT 
                    c.first_name,
                    c.last_name,
                    c.company_name,
                    v.client_id,
                    v.timestamp
                FROM visit AS v
                INNER JOIN client AS c
                    ON v.client_id = c.client_id
                WHERE v.subscription_id = ?;
            '''
        if get_count:

            query = '''
                SELECT 
                    c.first_name,
                    c.last_name,
                    c.company_name,
                    COUNT(v.timestamp) AS visit_count
                FROM visit AS v
                INNER JOIN client AS c
                    ON v.client_id = c.client_id
                WHERE v.subscription_id = ?
                GROUP BY c.client_id, c.first_name, c.last_name, c.company_name;
            '''
        
        result = cls.custom(query=query, values=(sub_id,), col_names=col_names, many=True, result_only=result_only)

        if col_names:
            return result
        return result[0]

    @classmethod
    def get_client_visits(cls, client_id: str, get_count: bool=False, col_names=False) -> list:
        
        query = '''
                SELECT
                    c.first_name,
                    c.last_name,
                    c.company_name,
                    v.client_id,
                    v.timestamp
                FROM visit AS v
                INNER JOIN client AS c
                    ON v.client_id = c.client_id
                WHERE v.client_id = ?;
            '''
        if get_count:

            query = '''
                SELECT 
                    c.first_name,
                    c.last_name,
                    c.company_name,
                    COUNT(v.timestamp) AS visit_count
                FROM visit AS v
                INNER JOIN client AS c
                    ON v.client_id = c.client_id
                WHERE v.subscription_id = ?
                GROUP BY c.client_id, c.first_name, c.last_name, c.company_name;
            '''

        result = cls.custom(cls, query, values=(client_id,), col_names=col_names, many=True)

        if col_names:
            return result
        
        return result[0]

    @classmethod  
    def filter_sub(cls, value, col_names: bool=False):

        query = '''
            SELECT 
                c.first_name,
                c.last_name,
                c.company_name,
                v.client_id,
            FROM client AS c
            INNER JOIN visit AS v
                ON c.client_id = v.client_id
            WHERE timestamp LIKE ?
        '''

        result = cls.custom(cls, query, values=(f'%{value}%',), col_names=col_names, many=True)

        if col_names:
            return result
        
        return result[0]
       
    @classmethod
    def get_all_sub_visits_count(cls, sub_id) -> list:
        query = '''
            SELECT
                v.client_id
            FROM visit AS v
            WHERE v.subscription_id = ?;
        '''

        result = cls.custom(query=query, values=(sub_id,), many=True, result_only=True)
        return len(result)

    @classmethod
    def export_visits(cls, path, sub_id: str, using=None):

        visits_by_date, column_names_by_date = Visit.get_client_visits_per_sub(sub_id, col_names=True)
        visits_by_count, column_names_by_count = Visit.get_client_visits_per_sub(sub_id, get_count=True, col_names=True)

        column_names_by_date = column_names_by_date if column_names_by_date else None
        column_names_by_count = column_names_by_count if column_names_by_count else None

        # remove unnecessary data like subcription_id
        formated_visits_by_date = []
        formated_visits_by_count = []

        for visit in visits_by_date:
            visit = list(visit)
            # remove client id
            visit.pop(3)
            formated_visits_by_date.append(visit)

        for visit in visits_by_count:
            visit = list(visit)
            formated_visits_by_count.append(visit)

        # remove client id from header
        column_names_by_date.pop(3)

        formatted_visit_by_date_header = []
        formatted_visit_by_count_header = []
        
        for header in column_names_by_date:
            header = header.replace('_', ' ').upper()
            formatted_visit_by_date_header.append(header)
            
        for header in column_names_by_count:
            header = header.replace('_', ' ').upper()
            formatted_visit_by_count_header.append(header)

        data_by_date = {
            'entries': formated_visits_by_date,
            'headers': formatted_visit_by_date_header
        }

        data_by_count = {
            'entries': formated_visits_by_count,
            'headers': formatted_visit_by_count_header
        }

        export_helper(cls, '.pdf', path, data=data_by_date, name='visits_by_date_export', )
        export_helper(cls, '.pdf', path, data=data_by_count, name='visits_by_count_export', )
        print('Export complete')
        


