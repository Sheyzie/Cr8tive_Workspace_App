import time
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



class Client(InitDB):

    def __init__(self, using=None, **kwargs):
        super().__init__(using=using)
        self.client_id = None
        self.first_name = None
        self.last_name = None
        self.company_name = None
        self.email = None
        self.phone = None
        self.created_at = None
        self.query = ""
        data = kwargs.get('kwargs')
        if kwargs:
            self._get_from_kwargs(kwargs=data)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def __str__(self):
        return f'{self.first_name} {self.last_name}' if self.first_name else self.company_name

    def _get_from_kwargs(self, **kwargs):
        data = kwargs.get('kwargs')
        client_id = data.get('client_id')
        if client_id:
            self.client_id = client_id

        first_name = data.get('first_name')
        if first_name:
            self.first_name = first_name.strip()

        last_name = data.get('last_name')
        if last_name:
            self.last_name = last_name.strip()

        company_name = data.get('company_name')
        if company_name:
            self.company_name = company_name.strip()

        email = data.get('email')
        if email:
            self.email = email.strip().lower()

        phone = data.get('phone')
        if phone:
            self.phone = phone.strip()

        created_at = data.get('created_at')
        if created_at:
            self.created_at = created_at

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
                raise ValidationError('Client ID cannot be empty')
            
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('client', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Client ID')
            
            self.client_id = id_string
            
            log_to_file('Client', 'Success', 'Client ID generated')
            
            cursor.close()
            self.conn.close()

    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.first_name, self.last_name, self.company_name, self.email, self.phone, self.client_id)
                    update_in_db('client', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return
             
                values = (self.client_id, self.first_name, self.last_name, self.company_name, self.email, self.phone, created_at)
                insert_to_db('client', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                log_error_to_file('Client', 'Error', f'Error saving client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error saving client')
                Notification.send_notification(err)
                       
    def update(self):
        self._validate(check_id=True)
        self.save_to_db(update=True)

    def delete(self):
        self._validate(check_id=True)
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            self.query = '''
                DELETE FROM client WHERE client_id = ?;
            '''

            try:
                cursor.execute(self.query, (self.client_id,))
                self.conn.commit()
                self.conn.close()
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error deleting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error deleting client')
                Notification.send_notification(err)

    @classmethod
    def fetch_one(cls, value, by_phone=False, by_email=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
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
                'created_at': client_data[6],
            }

            if client_data:
                client = Client(kwargs=client_data_obj, using=using)
                return client
            else:
                return None
        except Exception as err:
            log_error_to_file('Client', 'Error', f"Error getting client @ {__name__} 'line 163'")
            log_error_to_file('Client', 'Error', f'{err}')
            log_to_file('Client', 'Error', f"Error getting client @ {__name__} 'line 163'")
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls, col_names=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
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
                    'created_at': client_data[6],
                }

                client = Client(kwargs=client_data_obj, using=using)
                clients.append(client)

            return clients
        except Exception as err:
            log_error_to_file('Client', 'Error', f"Error getting client @ {__name__} 'line 179'")
            log_error_to_file('Client', 'Error', f'{err}')
            log_to_file('Client', 'Error', f"Error getting client @ {__name__} 'line 179'")
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_client(cls, value, name=False, created_at=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
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

                if created_at:
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
                        'created_at': client_data[6],
                    }

                    client = Client(kwargs=client_data_obj, using=using)
                    clients.append(client)

                

                return clients
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error getting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error getting client')
                Notification.send_notification(err)
                return None
        
    @classmethod
    def import_clients(cls, filepath, file_type, has_header, using=None):
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
                    client = Client(kwargs=data, using=using)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((data, {'Reason': err}))
                    print(err)
                    Notification.send_notification(err)

        elif has_header and file_type.lower() == '.csv':
            for client_data in manager.import_from_csv():
                
                try:
                    client = Client(kwargs=client_data, using=using)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

        elif file_type.lower() == '.xlsx':
            for client_data in manager.import_from_excel():
                
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4]
                }

                try:
                    client = Client(kwargs=data, using=using)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

        else:
            for client_data in manager.import_from_pdf():
                data = {
                    'first_name': client_data[0],
                    'last_name': client_data[1],
                    'company_name': client_data[2],
                    'email': client_data[3],
                    'phone': client_data[4]
                }
                try:
                    client = Client(kwargs=data, using=using)
                    client.get_id()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))
                    Notification.send_notification(err)

    @classmethod
    def export_clients(cls, file_type, path, using=None):
        export_helper(cls, file_type, path, 'clients_export', using=using)
        print('Export complete')
        
