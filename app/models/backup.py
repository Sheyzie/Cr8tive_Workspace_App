import time
import inspect
from typing import Self
from database.db import InitDB
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper

import logging

logger = logging.getLogger(__name__)



class Backup(InitDB):
    """
    Backup model for the backup table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    """
    model_name = 'backup'

    def __init__(self, using=None, **kwargs):
        super().__init__()
        self.backup_id = None
        self.timestamp = None
        # self.client_id: str = None
        
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
        return self.model_name
    

    def _reset_fields(self):
        """
        Reset all field
        """
        self.backup_id = None
        self.timestamp = None

    def _get_from_kwargs(self, **kwargs) -> None:
      self.backup_id = kwargs.get('field', None)
      self.timestamp = kwargs.get('field', None)


    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

