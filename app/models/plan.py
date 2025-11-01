import time
from database.db import InitDB
from exceptions.exception import ValidationError, GenerationError
from logs.utils import log_error_to_file, log_to_file
from utils.import_file import ImportManager
from helpers.export_helper import export_helper
from helpers.db_helpers import generate_id
from notification.notification import Notification
from helpers.db_helpers import (
    generate_id, 
    insert_to_db, 
    update_in_db, 
    fetch_one_entry, 
    fetch_all_entry
)



class Plan(InitDB):
    def __init__(self, using=None, **kwargs):
        super().__init__(using=using)
        self.plan_id = None
        self.plan_name = None
        self.duration = None
        self.plan_type = None
        self.price = None
        self.created_at = None
        data = kwargs.get('kwargs')
        if kwargs:
            self._get_from_kwargs(kwargs=data)
        try:
            self._validate()
        except ValidationError as err:
            Notification.send_notification(err)

    def __str__(self):
        return self.plan_name

    def _get_from_kwargs(self, **kwargs):
        data = kwargs.get('kwargs')
        plan_id = data.get('plan_id')
        if plan_id:
            self.plan_id = plan_id

        plan_name = data.get('plan_name')
        if plan_name:
            self.plan_name = plan_name.strip()

        duration = data.get('duration')
        if duration:
            self.duration = duration
        
        plan_type = data.get('plan_type')
        if plan_type:
            self.plan_type = plan_type.strip()

        price = data.get('price')
        if price:
            self.price = price

        created_at = data.get('created_at')
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
        
        if check_id:
            if not self.plan_id:
                raise ValidationError('Plan ID is required')
        
    def get_id(self):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            id_string = generate_id('payment', cursor)
            
            if not id_string:
                raise GenerationError('Error generating Plan ID')
            
            self.plan_id = id_string
            
            log_to_file('Plan', 'Success', f'Plan ID generated')
            
            cursor.close()
            self.conn.close()
   
    def save_to_db(self, update=False):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    values = (self.plan_name, self.duration, self.plan_type, self.price, self.plan_id)
                    update_in_db('plan', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                values = (self.plan_id, self.plan_name, self.duration, self.plan_type, self.price, created_at)
                insert_to_db('plan', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                log_error_to_file('Plan', 'Error', f'Error saving plan')
                log_error_to_file('Plan', 'Error', f'{err}')
                log_to_file('Plan', 'Error', f'Error saving plan')
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
                DELETE FROM plan WHERE plan_id = ?;
            '''

            try:
                cursor.execute(self.query, (self.plan_id,))
                self.conn.commit()
                self.conn.close()
            except Exception as err:
                log_error_to_file('Plan', 'Error', f'Error deleting plan')
                log_error_to_file('Plan', 'Error', f'{err}')
                log_to_file('Plan', 'Error', f'Error deleting plan')
                Notification.send_notification(err)

    @classmethod
    def fetch_one(cls, value, by_name=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        
        try:
            plan_data = fetch_one_entry('plan', cursor, value, by_name)
            
            if plan_data is None:
                return None
            
            plan_data_obj = {
                'plan_id': plan_data[0],
                'plan_name': plan_data[1],
                'duration': plan_data[2],
                'plan_type': plan_data[3],
                'price': plan_data[4],
                'created_at': plan_data[5],
            }

            if plan_data:
                plan = Plan(kwargs=plan_data_obj, using=using)
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
    def fetch_all(cls, col_names=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        cursor = conn.cursor()
        plans = []
        try:
            plans_data = fetch_all_entry('plan', cursor, col_names=col_names)
            
            if not len(plans_data) > 0:
                return []
            
            # only exports will set col_name to true so no need to create client obj
            if col_names:
                return plans_data
            for plan_data in plans_data:
                plan_data_obj = {
                    'plan_id': plan_data[0],
                    'plan_name': plan_data[1],
                    'duration': plan_data[2],
                    'plan_type': plan_data[3],
                    'price': plan_data[4],
                    'created_at': plan_data[5],
                }

                plan = Plan(kwargs=plan_data_obj, using=using)
                plans.append(plan)

            return plans
        except Exception as err:
            log_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

    @classmethod  
    def filter_plan(cls, value, plan_type=False, created_at=False, using=None):
        if using:
            # give class the datebase property to enable db connection
            cls._db = using + '.db'
        conn = cls._connect_to_db(cls)
        plans = []
        try:
            if conn:
                cursor = conn.cursor()
                if plan_type:
                    query = '''
                        SELECT * FROM plan WHERE plan_type = ?;
                    '''
                    cursor.execute(query, (value,))

                if created_at:
                    query = '''
                        SELECT * FROM plan WHERE created_at LIKE ?;
                    '''
                    cursor.execute(query, ('%' + value + '%',))

                plans_data = cursor.fetchall()

                if not len(plans_data) > 0:
                    return []
                
                for plan_data in plans_data:
                    plan_data_obj = {
                        'plan_id': plan_data[0],
                        'plan_name': plan_data[1],
                        'duration': plan_data[2],
                        'plan_type': plan_data[3],
                        'price': plan_data[4],
                        'created_at': plan_data[5],
                    }

                    plan = Plan(kwargs=plan_data_obj, using=using)
                    plans.append(plan)

                return plans
        except Exception as err:
            log_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'Error getting plan from db')
            log_error_to_file('Plan', 'Error', f'{err}')
            Notification.send_notification(err)
            return None

        
    @classmethod
    def import_plans(cls, filepath, file_type, has_header, using=None):
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
                    plan = Plan(kwargs=data, using=using)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((data, {'Reason': err}))
                    Notification.send_notification(err)

        elif has_header and file_type.lower() == '.csv':
            for plan_data in manager.import_from_csv():
                
                try:
                    plan = Plan(kwargs=plan_data, using=using)
                    plan.get_id()
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
                    plan = Plan(kwargs=data, using=using)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))
                    Notification.send_notification(err)

        else:
            for plan_data in manager.import_from_pdf():
                data = {
                    'plan_name': plan_data[0],
                    'duration': plan_data[1],
                    'plan_type': plan_data[2],
                    'price': plan_data[3],
                }

                try:
                    plan = Plan(kwargs=data, using=using)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed.append((plan_data, {'Reason': err}))
                    Notification.send_notification(err)

    @classmethod
    def export_plans(cls, file_type, path, using=None):
        export_helper(cls, file_type, path, 'plans_export', using=using)
        print('Export complete')

