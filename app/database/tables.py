import uuid

from .db import InitDB
from app.exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager


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
        self._validate()

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
            
    def register(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            user_found = True

            while user_found:
                try:
                    id_string = str(uuid.uuid4())
                    self.query = '''
                        SELECT * FROM client WHERE client_id = %s
                    '''
                    cursor.execute(self.query, (id_string,))
                    client = cursor.fetchone()
                    
                    if not client:
                        user_found = False
                        self.client_id = id_string
                except Exception as err:
                    log_error_to_file('Client', 'Error', f'Error getting user')
                    log_error_to_file('Client', 'Error', f'{err}')
                    log_to_file('Client', 'Error', f'Error getting user')

            self.query = ""
            cursor.close()
            self.conn.close()

    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)

            self.query = '''
                INSERT INTO client VALUES (%s, %s, %s, %s, %s, %s);
            '''

            value = (self.client_id, self.first_name, self.last_name, self.company_name, self.email, self.phone)

            if update:
                self.query = '''
                    UPDATE client SET first_name = %s, last_name = %s, company_name = %s, email = %s, phone = %s WHERE client_id = %s;
                '''
                value = (self.first_name, self.last_name, self.company_name, self.email, self.phone, self.client_id)

            try:
                cursor.execute(self.query, value)
                self.query = ""
            except Exception as err:
                    log_error_to_file('Client', 'Error', f'Error inserting client')
                    log_error_to_file('Client', 'Error', f'{err}')
                    log_to_file('Client', 'Error', f'Error inserting client')

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

    @classmethod
    def fetch_all(cls):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = '''
                SELECT * FROM client;
            '''

            try:
                cursor.execute(query)

                clients = cursor.fetchall()

                return clients
            except Exception as err:
                log_error_to_file('Client', 'Error', f'Error getting client')
                log_error_to_file('Client', 'Error', f'{err}')
                log_to_file('Client', 'Error', f'Error getting client')

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

        elif has_header and file_type.lower() == '.csv':
            for client_data in manager.import_from_csv():
                
                try:
                    client = Client(client_data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))

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

        else:
            for client_data in manager.import_from_pdf():
                try:
                    client = Client(client_data)
                    client.register()
                    client.save_to_db()
                    clients.append(client)
                except Exception as err:
                    failed.append((client_data, {'Reason': err}))

    @classmethod
    def export_clients(cls, file_type):
        ACCEPTED_TYPES = {'.csv', '.pdf', '.xls', '.xlsx'}

        if file_type not in ACCEPTED_TYPES:
            raise ValidationError(f'File type: {file_type} not valid. Valid types include {', '.join(ACCEPTED_TYPES)}')
        file_name = 'clients_export' + file_type
        pass
        

class Plan(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.plan_id = None
        self.plan_name = None
        self.duration = None
        self.type = None
        self.price = None
        self.created_at = None
        if kwargs:
            self._get_from_kwargs(kwargs)
        self._validate()

    def _get_from_kwargs(self, **kwargs):
        plan_id = kwargs.get('plan_id')
        if plan_id:
            self.plan_id = plan_id

        plan_name = kwargs.get('plan_name')
        if plan_name:
            self.plan_name = plan_name.strip()

        duration = kwargs.get('duration')
        if duration:
            self.duration = duration
        
        plan_type = kwargs.get('type')
        if plan_type:
            self.type = plan_type.strip()

        price = kwargs.get('price')
        if price:
            self.price = price

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False):
        VALID_PLAN_TYPES = {'hourly', 'daily', 'weekly', 'monthly', 'yearly'}

        if not self.plan_name:
            raise ValidationError('Plan name cannot be less than three letters')
        if len(self.plan_name) < 3:
            raise ValidationError('Plan name cannot be less than three letters')
        if not isinstance(self.duration, (int, float)):
            raise ValidationError('Plan duration cannot be letters')
        if self.duration < 1:
            raise ValidationError('Plan cannot be less than 1')
        if self.type not in VALID_PLAN_TYPES:
            raise ValidationError(f'Plan type: {self.type} is not valid. Must be one of {', '.join(VALID_PLAN_TYPES)}')
        if not isinstance(self.price, (int, float)):
            raise ValidationError('Price cannot have letters')
        if self.price < 0:
            raise ValidationError('Price cannot be negative')
        
    def add_plan(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            plan_found = True

            while plan_found:
                try:
                    id_string = str(uuid.uuid4())
                    self.query = '''
                        SELECT * FROM plan WHERE plan_id = %s
                    '''
                    cursor.execute(self.query, (id_string,))
                    client = cursor.fetchone()
                    
                    if not client:
                        plan_found = False
                        self.plan_id = id_string
                except Exception as err:
                    log_error_to_file('Plan', 'Error', f'Error getting plan')
                    log_error_to_file('Plan', 'Error', f'{err}')
                    log_to_file('Plan', 'Error', f'Error getting plan')

            self.query = ""
            cursor.close()
            self.conn.close()

        
    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)

            self.query = '''
                INSERT INTO plan VALUES (%s, %s, %s, %s, %s);
            '''

            value = (self.plan_id, self.plan_name, self.duration, self.type, self.price)

            if update:
                self.query = '''
                    UPDATE plan SET plan_name = %s, duration = %s, type = %s, price = %s WHERE plan_id = %s;
                '''
                value = (self.plan_name, self.duration, self.type, self.price, self.plan_id)

            try:
                cursor.execute(self.query, value)
                self.query = ""
            except Exception as err:
                    log_to_file('Plan', 'Error', f'Error saving plan to db')
                    log_error_to_file('Plan', 'Error', f'Error saving plan to db')
                    log_error_to_file('Plan', 'Error', f'{err}')
                     
    @classmethod
    def fetch_one(cls, value, by_name=False):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = '''
                SELECT * FROM plan WHERE plan_id = %s;
            '''

            if by_name:
                query = '''
                    SELECT * FROM plan WHERE plan_name = %s;
                '''
            try:
                cursor.execute(query, (value,))

                data = cursor.fetchone()

                if data:
                    plan = Plan(**data)
                    return plan
                else:
                    return None
            except Exception as err:
                log_to_file('Plan', 'Error', f'Error getting plan from db')
                log_error_to_file('Plan', 'Error', f'Error getting plan from db')
                log_error_to_file('Plan', 'Error', f'{err}')
                return None

    @classmethod
    def fetch_all(cls):
        conn = cls._connect_to_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = '''
                SELECT * FROM plan;
            '''
            try:
                cursor.execute(query)

                plans = cursor.fetchall()

                return plans
            except Exception as err:
                log_to_file('Plan', 'Error', f'Error getting plan from db')
                log_error_to_file('Plan', 'Error', f'Error getting plan from db')
                log_error_to_file('Plan', 'Error', f'{err}')
                return None

    @classmethod  
    def filter_plan(cls, value, plan_type=False, created_at=False):
        conn = cls._connect_to_db()
        try:
            if conn:
                cursor = conn.cursor(dictionary=True)
                if plan_type:
                    query = '''
                        SELECT * FROM plan WHERE type = %s;
                    '''
                    cursor.execute(query, (value,))

                if created_at:
                    query = '''
                        SELECT * FROM plan WHERE created_at LIKE %s;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                clients = cursor.fetchall()

                return clients
        except Exception as err:
            log_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'{err}')
            return None

        
    @classmethod
    def import_plans(cls, filepath, type):
        pass

    @classmethod
    def export_plans(cls, file_type):
        ACCEPTED_TYPES = {'.csv', '.pdf', '.xls'}

        if file_type not in ACCEPTED_TYPES:
            raise ValidationError(f'File type: {file_type} not valid. Valid types include {', '.join(ACCEPTED_TYPES)}')
        file_name = 'plans_export' + file_type
        pass