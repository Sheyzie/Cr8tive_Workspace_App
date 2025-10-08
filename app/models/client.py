import uuid
from pathlib import Path

from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id, insert_to_db, update_in_db
from notification.notification import Notification



class Client(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.client_id = None
        self.first_name = None
        self.last_name = None
        self.company_name = None
        self.email = None
        self.phone = None
        self.created_at = None
        self.query = ""
        if kwargs:
            self._get_from_kwargs(kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def _get_from_kwargs(self, **kwargs):
        client_id = kwargs.get('client_id')
        if client_id:
            self.client_id = client_id
        first_name = kwargs.get('first_name')
        if first_name:
            self.first_name = first_name.strip()

        last_name = kwargs.get('last_name')
        if last_name:
            self.last_name = last_name.strip()

        company_name = kwargs.get('company_name')
        if company_name:
            self.company_name = company_name.strip()

        email = kwargs.get('email')
        if email:
            self.email = email.strip().lower()

        phone = kwargs.get('phone')
        if phone:
            self.phone = phone.strip()

    def _validate(self, check_id=False):
        # validating first_name and company name
        if not self.first_name and not self.company_name:
            raise ValidationError('First Name and Company Name cannot both be empty')
        if self.first_name and len(self.first_name) < 3:
            raise ValidationError('First Name cannot be less than 3 characters')
        if self.company_name and len(self.company_name) < 3:
            raise ValidationError('Company Name cannot be less than 3 characters')

        
        # validating phone
        if not self.phone:
            raise ValidationError('Phone cannot be empty')
        
        if not self.phone.isdigit():
            raise ValidationError('Phone cannot contain alphabet')
        
        # validating check_id
        if check_id:
            if not self.client_id:
                raise ValidationError('Phone cannot be empty')
            
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            id_string = generate_id('payment', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Payment ID')
            
            self.payment_id = id_string
            
            log_to_file('Client', 'Success', f'Payment ID generated')
            
            cursor.close()
            self.conn.close()

    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            try:
                if update:
                    values = (self.first_name, self.last_name, self.company_name, self.email, self.phone, self.client_id)
                    update_in_db('client', cursor, values)
                    return

                values = (self.client_id, self.first_name, self.last_name, self.company_name, self.email, self.phone)
                insert_to_db('client', cursor, values)
            except ValueError as err:
                log_error_to_file('Client', 'Error', f'Error saving client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error saving client')
                Notification.send_notification(err)
            
    def update(self, **kwargs):
        if kwargs:
            self._get_from_kwargs(kwargs)
            self._validate(check_id=True)
            self.save_to_db(update=True)

    def delete(self):
        self._validate(check_id=True)
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            self.query = '''
                DELETE FROM client WHERE client_id = %s
            '''

            try:
                cursor.execute(self.query, (self.client_id,))
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error deleting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error deleting client')
                Notification.send_notification(err)

    @classmethod
    def fetch_one(cls, value, by_phone=False, by_email=False):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = '''
                SELECT * FROM client WHERE client_id = %s;
            '''

            if by_phone:
                query = '''
                    SELECT * FROM client WHERE phone = %s;
                '''

            if by_email:
                query = '''
                    SELECT * FROM client WHERE email = %s;
                '''

            try:
                cursor.execute(query, (value,))

                data = cursor.fetchone()

                if data:
                    client = Client(**data)
                    return client
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error getting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error getting client')
                Notification.send_notification(err)

    @classmethod
    def fetch_all(cls, col_names=False):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = '''
                SELECT * FROM client;
            '''

            try:
                cursor.execute(query)

                clients = cursor.fetchall()

                if col_names:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    clients = (clients, column_names)
                return clients if clients else []
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error getting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error getting client')
                Notification.send_notification(err)

    @classmethod  
    def filter_client(cls, value, name=False, created_at=False):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                if name:
                    query = '''
                        SELECT * FROM client WHERE first_name = %s OR last_name = %s OR company_name = %s;
                    '''
                    cursor.execute(query, (value, value, value))

                if created_at:
                    query = '''
                        SELECT * FROM client WHERE created_at LIKE %s;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                clients = cursor.fetchall()

                return clients
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error getting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error getting client')
                Notification.send_notification(err)
        
    @classmethod
    def import_clients(cls, filepath, file_type, has_header):
        manager = ImportManager(file_path=filepath, file_type=file_type, has_header=has_header)
        clients = []
        failed = []

        if not has_header and file_type.lower() == '.cvs':
            for client_data in manager.import_from_csv():
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4]
                }

                try:
                    client = Client(data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((data, {'Reason': err}))
                    Notification.send_notification(err)

        elif has_header and file_type.lower() == '.csv':
            for client_data in manager.import_from_csv():
                
                try:
                    client = Client(client_data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

        elif file_type.lower() in {'.xls', '.xlsx'}:
            for client_data in manager.import_from_excel():
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4]
                }
                try:
                    client = Client(client_data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

        else:
            for client_data in manager.import_from_pdf():
                try:
                    client = Client(client_data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

    @classmethod
    def export_clients(cls, file_type, path):
        export_helper(cls, file_type, path, 'clients_export')
        print('Export complete')
        

