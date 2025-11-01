from pathlib import Path
from exceptions.exception import ValidationError
from utils.export_file import ExportManager


def export_helper(cls, file_type, path, name, using=None):
    ACCEPTED_TYPES = {'.csv', '.pdf', '.xlsx'}

    if file_type not in ACCEPTED_TYPES:
        raise ValidationError(f'File type: {file_type} not valid. Valid types include {', '.join(ACCEPTED_TYPES)}')
    
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError('Invalid path')

    file = name + file_type

    file_name = file_path / file
   
    clients, column_names = cls.fetch_all(col_names=True, using=using)
    
    column_names = column_names if column_names else None

    # remove client_id and created_at
    formated_clients = []
    for client in clients:
        client = list(client)
        client.pop(0)
        client.pop(-1)
        formated_clients.append(client)
    
    column_names.pop(0)
    column_names.pop(-1)

    manager = ExportManager(file_name, file_type)

    if file_type == '.csv':
        manager.export_to_csv(formated_clients, column_names)
    elif file_type == '.xlsx':
        manager.export_to_excel(formated_clients, column_names)
    elif file_type == '.pdf':
        manager.export_to_pdf(formated_clients, column_names)