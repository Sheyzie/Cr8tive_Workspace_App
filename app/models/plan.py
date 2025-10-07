import uuid
from pathlib import Path

from database.db import InitDB
from exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from helpers.export_helper import export_helper
from notification.notification import Notification



class Plan(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.plan_id = None
        self.plan_name = None
        self.duration = None
        self.plan_type = None
        self.price = None
        self.created_at = None
        if kwargs:
            self._get_from_kwargs(kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

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
        
        plan_type = kwargs.get('plan_type')
        if plan_type:
            self.plan_type = plan_type.strip()

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
        if self.plan_type not in VALID_PLAN_TYPES:
            raise ValidationError(f'Plan type: {self.plan_type} is not valid. Must be one of {', '.join(VALID_PLAN_TYPES)}')
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
                    Notification.send_notification(err)

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

            value = (self.plan_id, self.plan_name, self.duration, self.plan_type, self.price)

            if update:
                self.query = '''
                    UPDATE plan SET plan_name = %s, duration = %s, type = %s, price = %s WHERE plan_id = %s;
                '''
                value = (self.plan_name, self.duration, self.plan_type, self.price, self.plan_id)

            try:
                cursor.execute(self.query, value)
                self.query = ""
            except Exception as err:
                    log_to_file('Plan', 'Error', f'Error saving plan to db')
                    log_error_to_file('Plan', 'Error', f'Error saving plan to db')
                    log_error_to_file('Plan', 'Error', f'{err}')
                    Notification.send_notification(err)
                     
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
                Notification.send_notification(err)
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
                Notification.send_notification(err)
                return None

    @classmethod  
    def filter_plan(cls, value, plan_type=False, created_at=False):
        conn = cls._connect_to_db()
        try:
            if conn:
                cursor = conn.cursor(dictionary=True)
                if plan_type:
                    query = '''
                        SELECT * FROM plan WHERE plan_type = %s;
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
            Notification.send_notification(err)
            return None

        
    @classmethod
    def import_plans(ccls, filepath, file_type, has_header):
        manager = ImportManager(file_path=filepath, file_type=file_type, has_header=has_header)
        plans = []
        failed = []

        if not has_header and file_type.lower() == '.cvs':
            for plan_data in manager.import_from_csv():
                data = {
                    'plan_name': plan_data[0],
                    'duration': plan_data[1],
                    'plan_type': plan_data[2],
                    'price': plan_data[3],
                }

                try:
                    plan = Plan(data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((data, {'Reason': err}))
                    Notification.send_notification(err)

        elif has_header and file_type.lower() == '.csv':
            for plan_data in manager.import_from_csv():
                
                try:
                    plan = Plan(data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))
                    Notification.send_notification(err)

        elif file_type.lower() in {'.xls', '.xlsx'}:
            for plan_data in manager.import_from_excel():
                data = {
                    'plan_name': plan_data[0],
                    'duration': plan_data[1],
                    'plan_type': plan_data[2],
                    'price': plan_data[3],
                }
                try:
                    plan = Plan(data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))
                    Notification.send_notification(err)

        else:
            for plan_data in manager.import_from_pdf():
                try:
                    plan = Plan(plan_data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))
                    Notification.send_notification(err)

    @classmethod
    def export_clients(cls, file_type, path):
        export_helper(cls, file_type, path, 'clients_export')
        print('Export complete')

