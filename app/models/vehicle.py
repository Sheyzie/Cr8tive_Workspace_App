import time
import inspect
from typing import Self
from database.db import InitDB
from database import fields
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper

import logging

logger = logging.getLogger(__name__)



class Vehicle(InitDB):
    """
    Vehicle model for the vehicle table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    """
    model_name = 'vehicle'
    vehicle_id = fields.UUIDField(pk = True, unique = True, null = False)
    client_id = fields.ForeignKeyField(pk = False, unique = False, null = False, to = 'client', on_delete = 'cascade', on_update = 'no action', pk_only = True)
    plate_number = fields.TextField(pk = False, unique = False, null = False)
    created_at = fields.DateTimeField(pk = False, unique = False, null = False, on_update = True)

    def __init__(self, using=None, **kwargs):
        super().__init__(**kwargs)
        
        try:
            self._validate()
        except ValidationError as err:
            self._reset_fields()
            logger.exception(str(err.message))
            self.write_error(str(err.message))
            raise err

    def __str__(self):
        return self.model_name

    def _get_from_kwargs(self, **kwargs) -> None:
        self.vehicle_id = kwargs.get('vehicle_id', None)
        self.client_id = kwargs.get('client_id', None)
        self.plate_number = kwargs.get('plate_number', None)
        self.created_at = kwargs.get('created_at', None)


    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

