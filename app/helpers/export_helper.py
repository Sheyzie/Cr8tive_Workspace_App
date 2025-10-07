from pathlib import Path
from exceptions.exception import ValidationError
from utils.export_file import ExportManager


def export_helper(cls, file_type, path, name):
    ACCEPTED_TYPES = {'.csv', '.pdf', '.xlsx'}

    if file_type not in ACCEPTED_TYPES:
        raise ValidationError(f'File type: {file_type} not valid. Valid types include {', '.join(ACCEPTED_TYPES)}')
    
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError('Invalid path')

    file = name + file_type

    file_name = file_path / file
    
    clients, column_name = cls.fetch_all(col_names=True)
    column_name = column_name if column_name else None

    manager = ExportManager(file_name, file_type)

    if file_type == '.csv':
        manager.export_to_csv(clients, column_name)
    elif file_type == '.xlsx':
        manager.export_to_excel(clients, column_name)
    elif file_type == '.pdf':
        manager.export_to_pdf(clients, column_name)