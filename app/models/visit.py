
import time
import inspect
from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from notification.notification import Notification
from helpers.db_helpers import insert_to_db

import logging


logger = logging.getLogger(__name__)


class Visit(InitDB):
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
            logger.error(str(err.message))
            self.stderr.write('\033[31m' + str(err.message + '\033[0m\n'))
            self.stderr.flush()
            Notification.send_notification(err)
            exit(1)

    def __str__(self):
        return f'{self.client.get_diaplay_name()} visited on {self.timestamp}'

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

        client = Client.fetch_one(kwargs.get('client_id'))
        if client:
            self.client = client

        subscription = Subscription.fetch_one(kwargs.get('subscription_id'))
        if subscription:
            self.subscription = subscription

    def _validate(self, check_id=False) -> None:
        from .client import Client
        from .subscription import Subscription

        if check_id:
            if not self.check_id:
                raise ValidationError('Visit not set')
            self._check_visit_id()

        if not self.client:
            raise ValidationError('Client not set visit')
        if not isinstance(self.client, Client):
            raise ValidationError('Client is not valid on visit')
        if not self.subscription:
            raise ValidationError('Subscription not set on visit')
        if not isinstance(self.subscription, Subscription):
            raise ValidationError('Subscription is not valid on visit')
        
    def get_id(self) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('visit', cursor)
            
            if not id_string:
                logger.warn('ID not generated')
                self.stderr.write('\033[31m' + 'ID not generated'+ '\033[0m\n')
                self.stderr.flush()
            
            self.visit_id = id_string
            
            cursor.close()
            self.conn.close()

    def _check_visit_id(self):
        '''
        check if id changed
        '''
        visit = Visit.fetch_one(self.visit_id)

        if not visit:
            raise ValidationError('Invalid ID for visit')
     
    def save_to_db(self) -> None:
        conn = self._connect_to_db()
        cursor = conn.cursor()
        if conn:
            self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:

                values = (self.visit_id, self.subscription.subscription_id, self.client.client_id, self.timestamp)
                insert_to_db('visit', cursor, values)
                conn.commit()
                conn.close()
                self.stderr.write(f'{self.client.get_display_name()} logged in to {self.subscription.plan.plan_name} plan successfully at {self.timestamp}')
                self.stderr.flush()
                Notification.send_notification('User logged in successfully')
            except ValueError as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()
                Notification.send_notification(err)

    def delete(self):
        conn = self._connect_to_db()
        cursor = conn.cursor()

        query = '''
            DELETE FROM visit WHERE visit_id = ?;
        '''

        try:
            cursor.execute(query, (self.visit_id,))
            conn.commit()
            conn.close()
            self.stderr.write(f'{self.client.get_display_name()} entry for {self.timestamp} deleted successfully')
            self._reset_fields()
        except Exception as err:
            logger.warn(str(err))
            self.stderr.write(str(err))
            self.stderr.flush()
            Notification.send_notification(err)

    @classmethod
    def get_client_visits_per_sub(cls, sub_id: str, get_count: bool=False, col_names=False) -> list:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        try:
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

            cursor.execute(query, (sub_id,))
            entries = cursor.fetchall()

            # return (subscriptions, column_names) for export
            if col_names:        
                column_names = [description[0] for description in cursor.description]        
                return (entries, column_names) if entries else []
            
            return entries
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []


    @classmethod
    def get_client_visits(cls, client_id: str, get_count: bool=False, col_names=False) -> list:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        try:
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

            cursor.execute(query, (client_id,))
            entries = cursor.fetchall()

            # return (subscriptions, column_names) for export
            if col_names:        
                column_names = [description[0] for description in cursor.description]        
                return (entries, column_names) if entries else []
            
            return entries
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    @classmethod  
    def filter_sub(cls, value, col_names: bool=False):
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        try:
            if conn:

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
                
                cursor.execute(query, ('%' + value + '%',))

                entries = cursor.fetchall()

                if col_names:
                # Get column names
                    column_names = [description[0] for description in cursor.description]

                    return (entries, column_names)

                return entries
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []


    @classmethod
    def get_all_sub_visits_count(cls, sub_id) -> list:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        try:
            query = '''
                SELECT
                    v.client_id
                FROM visit AS v
                WHERE v.subscription_id = ?;
            '''

            cursor.execute(query, (sub_id,))
            entries = cursor.fetchall()          
            return len(entries)

        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []


    @classmethod
    def export_visits(cls, path, sub_id: str, using=None):

        visits_by_date, column_names_by_date = Visit.get_client_visits_per_sub(sub_id, col_names=True, )
        visits_by_count, column_names_by_count = Visit.get_client_visits_per_sub(sub_id, get_count=True, col_names=True, )

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
        


