import time
import inspect
from typing import Self
from database.db import InitDB
from database import fields
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper

import logging

logger = logging.getLogger(__name__)



class Client(InitDB):
    '''
    Client model for the client table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    '''
    model_name = 'client'

    client_id = fields.UUIDField(pk=True, unique=True, null=False)
    first_name = fields.TextField(min_length=3)
    last_name = fields.TextField(min_length=3)
    company_name = fields.TextField()
    email = fields.TextField()
    phone = fields.TextField(null = False)
    display_name = fields.TextField(choice=['client', 'company'])
    created_at = fields.DateTimeField(on_save = True)
    updated_at = fields.DateTimeField(on_update = True)

    def __init__(self, using=None, **kwargs):
        super().__init__(**kwargs)

        try:
            self._validate()
        except ValidationError as err:
            # self._reset_fields()
            logger.exception(str(err.message))
            self.write_error(str(err.message))
            raise err

    def __str__(self):
        return f'{self.first_name} {self.last_name}' if self.first_name else self.company_name
        
    def get_display_name(self):
        if self._display_name == 'client':
            return f'{self.first_name} {self.last_name}'
        else:
            return self.company_name

    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)
        # validating first_name and company name
        if not self.first_name and not self.company_name:
            raise ValidationError('First Name and Company Name cannot both be empty')

        if self.first_name and len(self.first_name) < 3:
            raise ValidationError('First Name cannot be less than 3 characters')

        if self.company_name and len(self.company_name) < 3:
            raise ValidationError('Company Name cannot be less than 3 characters')

        # # validating phone
        # if not self.phone:
        #     raise ValidationError('Phone cannot be empty')
        
        # if not self.phone.isdigit():
        #     raise ValidationError('Phone cannot contain alphabet')
        
        # if self._display_name not in {'client', 'company'}:
        #     raise ValidationError('Display name needs either [client, company]')
        
        # validating check_id
        if check_id:
            if not self.client_id:
                raise ValidationError('Client ID cannot be empty')

            if not self._verify_pk():
                raise ValidationError('Client ID is not valid')

    # def save(self, update=False) -> None:
    #     super().save()
                       
    def update(self) -> None:
        self._validate(check_id=True)
        super().update()
    
