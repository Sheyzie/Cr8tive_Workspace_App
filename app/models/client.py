import time
import inspect
from typing import Self
from database.db import InitDB
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
        super()._validate(check_id)
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

            if not self._verify_pk():
                raise ValidationError('Client ID is not valid')

    # def save(self, update=False) -> None:
    #     super().save()
                       
    def update(self) -> None:
        self._validate(check_id=True)
        super().update()
    
