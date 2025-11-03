
import time
import inspect
from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from helpers.export_helper import export_helper
from notification.notification import Notification
from helpers.db_helpers import insert_to_db


class Visit(InitDB):
    def __init__(self, using: str=None, **kwargs):
        super().__init__(using=using)
        self.subscription_id: str = None
        self.client_id: str = None
        self.timestamp: str = None
        if kwargs:
            data = kwargs.get('kwargs')
            self._get_from_kwargs(kwargs=data)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)


    def _get_from_kwargs(self, **kwargs) -> None:
        data = kwargs.get('kwargs')
        subscription_id = data.get('subscription_id')
        if subscription_id:
            self.subscription_id = subscription_id
            
        client_id = data.get('client_id')
        if client_id:
            self.client_id = client_id


        timestamp = data.get('timestamp')
        if timestamp:
            self.timestamp = timestamp

    def _validate(self) -> None:
        if not self.subscription_id:
            raise ValidationError('Subscription ID is required')
        if not self.client_id:
            raise ValidationError('Client ID is required')
        if not self.timestamp:
            raise ValidationError('Timestamp is required')

    @classmethod   
    def save_to_db(cls, sub_id: str, client_id: str, using: str=None) -> None:
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        if conn:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:

                values = (sub_id, timestamp, client_id)
                insert_to_db('visit', cursor, values)
                conn.commit()
                conn.close()
                Notification.send_notification('User logged in successfully')
            except ValueError as err:
                log_error_to_file('Visit', 'Error', f"Error saving visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                log_error_to_file('Visit', 'Error', f'{err}')
                log_to_file('Visit', 'Error', f"Error saving visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
                Notification.send_notification(err)

    @classmethod
    def delete(cls, sub_id: str, client_id: str, date_value: str, using: str=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()

        query = '''
            DELETE FROM visit 
            WHERE 
                subscription_id = ? AND client_id = ? AND timestamp LIKE ?;
        '''

        try:
            cursor.execute(query, (sub_id, client_id, '%' + date_value + '%'))
            conn.commit()
            conn.close()
        except Exception as err:
            log_error_to_file('Visit', 'Error', f"Error deleting visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Visit', 'Error', f'{err}')
            log_to_file('Visit', 'Error', f"Error deleting visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)


    @classmethod
    def get_visits(cls, sub_id: str, get_count: bool=False, col_names=False, using: str=None) -> list:
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
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
                # query = '''
                #     SELECT client_id, Count(timestamp) FROM visit WHERE subscription_id = ? GROUP BY client_id;
                # '''
                query = '''
                    SELECT 
                        c.first_name,
                        c.last_name,
                        c.company_name,
                        v.client_id,
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
            log_to_file('Visit', 'Error', f"Error fetching visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Visit', 'Error', f"Error fetching visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Visit', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_sub(cls, value, col_names: bool=False, using: str=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using
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
                        ON c.id = v.client_id
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
            log_to_file('Visit', 'Error', f"Error fetching visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Visit', 'Error', f"Error fetching visit @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Visit', 'Error', f'{err}')
            Notification.send_notification(err)

    @classmethod
    def export_visits(cls, path, sub_id: str, using=None):

        visits_by_date, column_names_by_date = Visit.get_visits(sub_id, col_names=True, using=using)
        visits_by_count, column_names_by_count = Visit.get_visits(sub_id, get_count=True, col_names=True, using=using)

        column_names_by_date = column_names_by_date if column_names_by_date else None
        column_names_by_count = column_names_by_count if column_names_by_count else None

        # remove unnecessary data like subcription_id
        formated_visits_by_date = []
        formated_visits_by_count = []

        for visit in visits_by_date:
            visit = list(visit)
            # remove sub_id
            visit.pop(3)
            formated_visits_by_date.append(visit)

        for visit in visits_by_count:
            visit = list(visit)
            # remove sub_id
            visit.pop(3)
            formated_visits_by_count.append(visit)

        # remove sub_id header
        column_names_by_date.pop(3)
        column_names_by_count.pop(3)

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

        export_helper(cls, '.pdf', path, data=data_by_date, name='visits_by_date_export', using=using)
        export_helper(cls, '.pdf', path, data=data_by_count, name='visits_by_count_export', using=using)
        print('Export complete')
        


