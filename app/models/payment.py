import uuid
from pathlib import Path

from database.db import InitDB
from exceptions.exception import ValidationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from utils.export_file import ExportManager
from helpers.export_helper import export_helper
from notification.notification import Notification



class Payment(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.payment_id = None
        self.discount = None
        self.tax = None
        self.total_price = None
        self.amount_paid = None
        self.created_at = None
        if kwargs:
            self._get_from_kwargs(kwargs)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def _get_from_kwargs(self, **kwargs):
        payment_id = kwargs.get('payment_id')
        if payment_id:
            self.payment_id = payment_id

        discount = kwargs.get('discount')
        if discount:
            self.discount = discount

        tax = kwargs.get('tax')
        if tax:
            self.tax = tax
        
        total_price = kwargs.get('total_price')
        if total_price:
            self.type = total_price.strip()

        amount_paid = kwargs.get('amount_paid')
        if amount_paid:
            self.amount_paid = amount_paid

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False):
        VALID_PLAN_TYPES = {'hourly', 'daily', 'weekly', 'monthly', 'yearly'}

        if not self.discount:
            raise ValidationError('Payment discount is required')
        if self.discount < 0:
            raise ValidationError('Payment discount cannot be less than zero')
        if not isinstance(self.discount, (int, float)):
            raise ValidationError('Payment discount cannot be letters')
        if not self.tax:
            raise ValidationError('Payment tax is required')
        if self.tax < 0:
            raise ValidationError('Payment tax cannot be less than zero')
        if not isinstance(self.tax, (int, float)):
            raise ValidationError('Payment tax cannot be letters')
        if not self.total_price:
            raise ValidationError('Payment total_price is required')
        if self.total_price < 0:
            raise ValidationError('Payment total_price cannot be less than zero')
        if not isinstance(self.total_price, (int, float)):
            raise ValidationError('Payment total_price cannot be letters')
        if not self.amount_paid:
            raise ValidationError('Payment amount_paid is required')
        if self.amount_paid < 0:
            raise ValidationError('Payment amount_paid cannot be less than zero')
        if not isinstance(self.amount_paid, (int, float)):
            raise ValidationError('Payment amount_paid cannot be letters')
    
    # TODO: setup payment    
    def add_payment(self):
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

        elif has_header and file_type.lower() == '.csv':
            for plan_data in manager.import_from_csv():
                
                try:
                    plan = Plan(data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))

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

        else:
            for plan_data in manager.import_from_pdf():
                try:
                    plan = Plan(plan_data)
                    plan.register()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))


    @classmethod
    def export_clients(cls, file_type, path):
        export_helper(cls, file_type, path, 'clients_export')
        print('Export complete')

