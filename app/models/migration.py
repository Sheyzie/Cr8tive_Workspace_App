import time
import inspect
from typing import Self
from database.db import InitDB
from database import fields
from exceptions.exception import ValidationError
from helpers.export_helper import export_helper

import logging

logger = logging.getLogger(__name__)



class Migration(InitDB):
    """
    Migration model for the migration table
    - model_name must map to table name in TABLE_MAP
    - kwargs: {
            field_name: value
        }
    """
    model_name = 'migration'
    migration_id = fields.UUIDField(pk = True, unique = True, null = False)
    table_map = fields.JSONField(pk = False, unique = True, null = False, indent = 4)
    timestamp = fields.DateTimeField(pk = False, unique = False, null = False, on_update = True)

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
        self.migration_id = kwargs.get('migration_id', None)
        self.table_map = kwargs.get('table_map', None)
        self.timestamp = kwargs.get('timestamp', None)


    def _validate(self, check_id=False) -> None:
        super()._validate(check_id)

    def update(self) -> None:
        self._validate(check_id=True)
        super().update()

