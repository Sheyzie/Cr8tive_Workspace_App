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


class Plan(InitDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.plan_id: str = None
        self.plan_name: str = None
        self.duration: int = 0
        self.plan_type: str  = None
        self.slot: int = 0
        self.guest_pass: int = 0
        self.price: int = 0
        self.created_at: str = None
    
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

    def __str__(self) -> str:
        return self.plan_name
    
    def _reset_fields(self):
        '''
        Reset all field
        '''
        self.plan_id: str = None
        self.plan_name: str = None
        self.duration: int = 0
        self.plan_type: str  = None
        self.slot: int = 0
        self.guest_pass: int = 0
        self.price: int = 0
        self.created_at: str = None

    def _get_from_kwargs(self, **kwargs) -> None:
        plan_id = kwargs.get('plan_id', None)
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

        slot = kwargs.get('slot')
        if slot and isinstance(slot, (int, float)) and slot >= 0:
            self.slot = slot

        guest_pass = kwargs.get('guest_pass')
        if guest_pass and isinstance(guest_pass, (int, float)) and guest_pass >= 0:
            self.guest_pass = guest_pass

        price = kwargs.get('price')
        if price and isinstance(price, (int, float)) and price >= 0:
            self.price = price

        created_at = kwargs.get('created_at')
        if created_at:
            self.created_at = created_at

    def _validate(self, check_id=False) -> None:
        VALID_PLAN_TYPES = {'hourly', 'daily', 'weekly', 'monthly', 'half-year', 'yearly'}

        if not self.plan_name:
            raise ValidationError('Plan name is required')
        if len(self.plan_name) < 3:
            raise ValidationError('Plan name cannot be less than three letters')
        if not isinstance(self.duration, (int, float)):
            raise ValidationError('Plan duration cannot be letters')
        if self.duration < 1:
            raise ValidationError('Plan cannot be less than 1')
        if self.plan_type not in VALID_PLAN_TYPES:
            raise ValidationError(f'Plan type: {self.plan_type} is not valid. Must be one of {', '.join(VALID_PLAN_TYPES)}')
        if not isinstance(self.slot, (int, float)) and not self.slot >= 0:
            raise ValidationError('Slot cannot be less than zero')
        if not isinstance(self.guest_pass, (int, float)) and not self.guest_pass >= 0:
            raise ValidationError('Guest Pass cannot be less than zero')
        if not isinstance(self.price, (int, float)):
            raise ValidationError('Price cannot have letters')
        if self.price < 0:
            raise ValidationError('Price cannot be negative')
        
        if check_id:
            if not self.plan_id:
                raise ValidationError('Plan ID is required')
            self._check_plan_id()
        
    def get_id(self) -> None:
        self._connect_to_db()
        if self.conn:
            try:
                cursor = self.conn.cursor()
                id_string = generate_id('plan', cursor)
                
                if not id_string:
                    logger.warn('ID not generated')
                    self.stderr.write('\033[31m' + 'ID not generated'+ '\033[0m\n')
                    self.stderr.flush()
                
                self.plan_id = id_string
                
                cursor.close()
                self.conn.close()
            except Exception as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()
   
    def _check_plan_id(self):
        '''
        check if id changed
        '''
        plan = Plan.fetch_one(self.plan_id)

        if not plan:
            raise ValidationError('Invalid ID for plan')
        
        # if self.phone != client.phone:
        #     raise ValidationError('Client data do not match')

    def save_to_db(self, update=False) -> None:
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            try:
                if update:
                    # convert price to kobo
                    values = (self.plan_name, self.duration, self.plan_type, self.slot, self.guest_pass, (self.price * 100), self.plan_id)
                    update_in_db('plan', cursor, values)
                    self.conn.commit()
                    self.conn.close()
                    return

                # check if plam already exist with the plane_name 
                plan_exists = Plan.fetch_one(self.plan_name, True)
                if plan_exists:
                    self._reset_fields()
                    logger.warn('Plan already exist')
                    self.stderr.write(f"\nPlan already exist with {self.plan_name} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
                    self.stderr.flush()
                    Notification.send_notification(f'Plan already exist with {self.plan_name}')
                    return

                # convert price to kobo
                values = (self.plan_id, self.plan_name, self.duration, self.plan_type, self.slot, self.guest_pass, (self.price * 100), created_at)
                insert_to_db('plan', cursor, values)
                self.conn.commit()
                self.conn.close()
            except ValueError as err:
                logger.warn(str(err))
                self.stderr.write(str(err))
                self.stderr.flush()
                Notification.send_notification(err)
            
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
                    DELETE FROM plan WHERE plan_id = ?;
                '''

            cursor.execute(self.query, (self.plan_id,))
            self.conn.commit()
            self.conn.close()

            # reset fields
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
            Notification.send_notification(err)
            exit(1)

    @classmethod
    def fetch_one(cls, value, by_name=False) -> Self | None:
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
                'slot': plan_data[4],
                'guest_pass': plan_data[5],
                'price': float(plan_data[6]) / 100, # convert back from kobo
                'created_at': plan_data[7],
            }

            if plan_data:
                plan = Plan(**plan_data_obj)
                return plan
            else:
                return None
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return None

    @classmethod
    def fetch_all(cls, col_names=False) -> list:
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
                    'slot': plan_data[4],
                    'guest_pass': plan_data[5],
                    'price': float(plan_data[6]) / 100, # convert back from kobo
                    'created_at': plan_data[7],
                }

                plan = Plan(**plan_data_obj)
                plans.append(plan)
            
            return plans
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []

    @classmethod  
    def filter_plan(cls, value, plan_type=False, by_date=False) -> list:
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

                if by_date:
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
                        'slot': plan_data[4],
                        'guest_pass': plan_data[5],
                        'price': float(plan_data[6]) / 100, # convert back from kobo
                        'created_at': plan_data[7],
                    }

                    plan = Plan(**plan_data_obj)
                    plans.append(plan)

                return plans
        except Exception as err:
            logger.warn(str(err))
            cls.stderr.write(str(err))
            cls.stderr.flush()
            Notification.send_notification(err)
            return []
     
    @classmethod
    def import_plans(cls, filepath, file_type, has_header, using=None) -> None:
        manager = ImportManager(file_path=filepath, file_type=file_type, has_header=has_header)
        plans = []
        failed_imports = []
        data = {}

        if file_type.lower() == '.csv':
            for plan_data in manager.import_from_csv():
                if not has_header:
                    data = {
                        'plan_name': plan_data[0],
                        'duration': int(plan_data[1]),
                        'plan_type': plan_data[2],
                        'price': int(plan_data[3]),
                    }

                else:
                    data = plan_data
                    data['duration'] = int(data['duration'])
                    data['price'] = int(data['price'])

                try:
                    plan = Plan(**data)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed_imports.append((data, {'reason': err}))
                    continue

        elif file_type.lower() in {'.xls', '.xlsx'}:
            for plan_data in manager.import_from_excel():
                data = {
                    'plan_name': plan_data[0],
                    'duration': int(plan_data[1]),
                    'plan_type': plan_data[2],
                    'price': int(plan_data[3]),
                }
                try:
                    plan = Plan(**data)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed_imports.append((plan_data, {'reason': err}))
                    continue

        else:
            for plan_data in manager.import_from_pdf():
                data = {
                    'plan_name': plan_data[0],
                    'duration': int(plan_data[1]),
                    'plan_type': plan_data[2],
                    'price': int(plan_data[3]),
                }

                try:
                    plan = Plan(**data)
                    plan.get_id()
                    plan.save_to_db()
                    plans.append(plan)
                except Exception as err:
                    failed_imports.append((plan_data, {'reason': err}))
                    continue

        for i, failed_import in enumerate(failed_imports):
            cls.stdout.write(f'{i + 1} failed: {failed_import['reason']}')
            cls.stdout.flush()
        logger.info(f'({len(plans)}/ {len(plans) + len(failed_imports)} imported successfully)')
        cls.stdout.write(f'({len(plans)}/ {len(plans) + len(failed_imports)} imported successfully)')
        cls.stdout.flush()

    @classmethod
    def export_plans(cls, file_type, path) -> None:
        plans, column_names = Plan.fetch_all(col_names=True)

        column_names = column_names if column_names else None

        # remove unnecessary data like subcription_id
        formated_plans = []

        for plan in plans:
            plan = list(plan)
            plan.pop(0)
            formated_plans.append(plan)
        
        column_names.pop(0)

        formatted_header = []
        
        for header in column_names:
            if file_type == '.pdf':
                header = header.replace('_', ' ').upper()
            formatted_header.append(header)

        data = {
            'entries': formated_plans,
            'headers': formatted_header
        }

        export_helper(cls, file_type, path, data=data, name='plans_export')
        print('Export complete')


# https://www.cargopal.tonisoft.co.ke/

# Account: UAZ2MB
# Username: mzansilogisticske@gmail.com       password mwanikistan11