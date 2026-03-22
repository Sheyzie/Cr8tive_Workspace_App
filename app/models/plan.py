import time
import inspect
from typing import Self
from database.db import InitDB
from database.tables import TABLES_MAP
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
    '''
    Plan model for the plan table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    '''

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
            self.write_error(str(err.message))
            raise err

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
            try:
                # incase value is passed in as '1'
                self.duration = int(self.duration)
            except Exception as err:
                raise ValidationError(f'Plan duration cannot be letters got {self.duration}')
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
            if not self._verify_pk():
                raise ValidationError('Plan ID is not valid')

    def save_to_db(self, update=False) -> None:
        plan = Plan.fetch_one(plan_name=self.plan_name)

        if not update:
            if plan:
                self._reset_fields()
                logger.warn(f'Plan already exist with the name {plan.plan_name}')
                self.write_error(f"\nPlan already exist with {plan.plan_name} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")

                return
        super().save_to_db(update=update)
  
    def update(self) -> None:
        try:
            self._validate(check_id=True)
            self.save_to_db(update=True)
        except ValidationError as err:
            logger.error(str(err.message))
            self.write_error(str(err.message))
            raise err

# https://www.cargopal.tonisoft.co.ke/

# Account: UAZ2MB
# Username: mzansilogisticske@gmail.com       password mwanikistan11