from datetime import datetime
from uuid import UUID

TABLES_MAP = {
    "backup": {
        "backup": {
            "fields": {
                "backup_id": {
                    "is_pk": true,
                    "is_unique": true,
                    "is_nullable": false,
                    "datatype": "UUID"
                },
                "timestamp": {
                    "is_pk": false,
                    "is_unique": false,
                    "is_nullable": false,
                    "datatype": "datetime",
                    "is_date": true,
                    "auto_update": "save"
                }
            }
        }
    }
}
