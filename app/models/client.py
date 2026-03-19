import time
import inspect
from typing import Self
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

logger = logging.getLogger(__name__)



class Client(InitDB):
    '''
    Client model for the client table
    '''

    def __init__(self, using=None, **kwargs):
        super().__init__()
        self.client_id: str = None
        self.first_name: str = None
        self.last_name: str = None
        self.company_name: str = None
        self.email: str = None
        self.phone: str = None
        self.query = ""
        self._display_name: str = "client"
        self.created_at: str = None
        self.updated_at: str = None
        
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
        return f'{self.first_name} {self.last_name}' if self.first_name else self.company_name
    
    def get_display_name(self):
        if self._display_name == 'client':
            return f'{self.first_name} {self.last_name}'
        else:
            return self.company_name

    def _reset_fields(self):
        '''
        Reset all field
        '''
        self.client_id = None
        self.first_name = None
        self.last_name = None
        self.company_name = None
        self.email = None
        self.phone = None
        self.query = ""
        self._display_name = ""
        self.created_at = None
        self.updated_at = None

    def _get_from_kwargs(self, **kwargs) -> None:

        client_id = kwargs.get('client_id', None)
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

        display_name = kwargs.get('display_name')
        if display_name:
            self._display_name = display_name

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

        updated_at = kwargs.get('updated_at')
        if updated_at:
            self.updated_at = updated_at

    def _validate(self, check_id=False) -> None:
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
        
        if self._display_name not in {'client', 'company'}:
            raise ValidationError('Display name needs either [client, company]')
        
        # validating check_id
        if check_id:
            if not self.client_id:
                raise ValidationError('Client ID cannot be empty')

            self._check_user_id()
        
    def get_id(self) -> None:
        self._connect_to_db()
        if self.conn:
            try:
                cursor = self.conn.cursor()
                id_string = generate_id('client', cursor)
                
                if not id_string:
                    logger.warn('ID not generated')
                    self.stderr.write('\033[31m' + 'ID not generated'+ '\033[0m\n')
                    self.stderr.flush()
                
                self.client_id = id_string
                
                cursor.close()
                self.conn.close()
            except Exception as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()

    def _check_user_id(self):
        '''
        check if id changed
        '''
        client = Client.fetch_one(self.client_id)

        if not client:
            raise ValidationError('Invalid ID for client')
        
        # if self.phone != client.phone:
        #     raise ValidationError('Client data do not match')

    def save_to_db(self, update=False) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            updated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.first_name, self.last_name, self.company_name, self.email, self.phone, self._display_name, updated_at, self.client_id)
                    update_in_db('client', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                # check if user already exist with the phone number
                client_exist = Client.fetch_one(self.phone, True)
                if client_exist:
                    self._reset_fields()
                    logger.warn('User already exist')
                    self.stderr.write(f"\nUser already exist with {self.phone} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
                    self.stderr.flush()
                    Notification.send_notification(f'User already exist with {self.phone}')
                    return
                
                values = (self.client_id, self.first_name, self.last_name, self.company_name, self.email, self.phone, self._display_name, created_at, updated_at)
                insert_to_db('client', cursor, values)
                self.conn.commit()
                self.conn.close()

            except Exception as err:
                logging.error('Error saving client')
                self.stderr.write(str(err.with_traceback()))
                self.stderr.flush()
                Notification.send_notification('Unexpected error happened')
                       
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

    def delete(self) -> None:
        try:
            self._validate(check_id=True)
            self._connect_to_db()
            if self.conn:
                cursor = self.conn.cursor()
                self.query = '''
                    DELETE FROM client WHERE client_id = ?;
            '''

            cursor.execute(self.query, (self.client_id,))
            self.conn.commit()
            self.conn.close()

            # reset fields back
            self._reset_fields()
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
            Notification.send_notification('Unexpected error happened')

    @classmethod
    def fetch_one(cls, value, by_phone=False, by_email=False) -> Self | None:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        
        try:
            client_data = fetch_one_entry('client', cursor, value, by_phone=by_phone, by_email=by_email)

            if client_data is None:
                return None
            
            client_data_obj = {
                'client_id': client_data[0],
                'first_name': client_data[1],
                'last_name': client_data[2],
                'company_name': client_data[3],
                'email': client_data[4],
                'phone': client_data[5],
                'display_name': client_data[6],
                'created_at': client_data[7],
                'updated_at': client_data[8],
            }

            if client_data:
                client = Client(**client_data_obj)
                logger.info('Client fetched successfully')
                return client
            else:
                return None
        except Exception as err:
            logger.error('Error fetching client')
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification('Unexpected error happened')
            return None

    @classmethod
    def fetch_all(cls, col_names=False) -> list:
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        clients = []
        try:
            clients_data = fetch_all_entry('client', cursor, col_names=col_names)

            if not len(clients_data) > 0:
                return []
            
            # only exports will set col_name to true so no need to create client obj
            if col_names:
                return clients_data
            
            # create a client obj for each data
            for client_data in clients_data:
                client_data_obj = {
                    'client_id': client_data[0],
                    'first_name': client_data[1],
                    'last_name': client_data[2],
                    'company_name': client_data[3],
                    'email': client_data[4],
                    'phone': client_data[5],
                    'display_name': client_data[6],
                    'created_at': client_data[7],
                    'updated_at': client_data[8],
                }

                client = Client(**client_data_obj)
                clients.append(client)
            logger.info('Clients fetched successfully')
            return clients
        except Exception as err:
            logger.error('Error fetching client')
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification('Unexpected error happened')
            return []

    @classmethod  
    def filter_client(cls, value, name=False, by_date=False) -> list:
        conn = cls._connect_to_db(cls)
        clients = []
    
        if conn:
            cursor = conn.cursor()
            try:
                if name:
                    query = '''
                        SELECT * FROM client WHERE first_name = ? OR last_name = ? OR company_name = ?;
                    '''
                    cursor.execute(query, (value, value, value))

                if by_date:
                    query = '''
                        SELECT * FROM client WHERE created_at LIKE ?;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                clients_data = cursor.fetchall()

                if not len(clients_data) > 0:
                    return []
                
                # create a client obj for each data
                for client_data in clients_data:
                    client_data_obj = {
                        'client_id': client_data[0],
                        'first_name': client_data[1],
                        'last_name': client_data[2],
                        'company_name': client_data[3],
                        'email': client_data[4],
                        'phone': client_data[5],
                        'display_name': client_data[6],
                        'created_at': client_data[7],
                        'updated_at': client_data[8],
                    }

                    client = Client(**client_data_obj)
                    clients.append(client)
                logger.info('Clients fetched successfully')
                return clients
            except Exception as err:
                logger.error('Error fetching client')
                cls.stderr.write(str(err))
                cls.stderr.flush()
                Notification.send_notification('Unexpected error happened')
                return []
        
    @classmethod
    def import_clients(cls, filepath, file_type, has_header):
        logger.info('Importing clients from csv...')
        manager = ImportManager(file_path=filepath, file_type=file_type, has_header=has_header)
        clients = []
        failed_imports = []
        data = {}

        if file_type.lower() == '.csv':
            for client_data in manager.import_from_csv():
                if not has_header:
                    data = {
                        'first_name': client_data[0],
                        'last_name': client_data[1],
                        'company_name': client_data[2],
                        'email': client_data[3],
                        'phone': client_data[4],
                        'display_name': client_data[5],
                    }

                else:
                    data = client_data

                try:
                    client = Client(**data)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed_imports.append((data, {'reason': str(err)}))
                    continue

        elif file_type.lower() in {'.xls', '.xlsx'}:
            for client_data in manager.import_from_excel():
                
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4],
                    'display_name': client_data[5],
                }

                try:
                    client = Client(**data)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed_imports.append((client_data, {'reason': str(err)}))
                    Notification.send_notification(err)
                    continue

        else:
            for client_data in manager.import_from_pdf():
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4],
                    'display_name': client_data[5],
                }
                try:
                    client = Client(**data)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed_imports.append((client_data, {'reason': str(err)}))
                    Notification.send_notification(err)
                    continue
        for i, failed_import in enumerate(failed_imports):
            cls.stdout.write(f'{i + 1} failed: {failed_import['reason']}')
            cls.stdout.flush()
        logger.info(f'({len(clients)}/ {len(clients) + len(failed_imports)} imported successfully)')
        cls.stdout.write(f'({len(clients)}/ {len(clients) + len(failed_imports)} imported successfully)')
        cls.stdout.flush()

    @classmethod
    def export_clients(cls, file_type, path):

        clients, column_names = Client.fetch_all(col_names=True)

        column_names = column_names if column_names else None

        # remove unnecessary data like subcription_id
        formated_clients = []

        for client in clients:
            client = list(client)
            client.pop(0)
            formated_clients.append(client)
        
        column_names.pop(0)

        formatted_header = []
        
        for header in column_names:
            if file_type == '.pdf':
                header = header.replace('_', ' ').upper()
            formatted_header.append(header)
            

        data = {
            'entries': formated_clients,
            'headers': formatted_header
        }

        export_helper(cls, file_type, path, data=data, name='clients_export')
        print('Export complete')
        
