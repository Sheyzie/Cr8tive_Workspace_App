from pathlib import Path
from exceptions.exception import ValidationError
from utils.export_file import ExportManager


def export_helper(cls, file_type, path, data: dict[str, list]=None, name=None):
    ACCEPTED_TYPES = {'.csv', '.pdf', '.xlsx'}

    if file_type not in ACCEPTED_TYPES:
        raise ValidationError(f'File type: {file_type} not valid. Valid types include {', '.join(ACCEPTED_TYPES)}')
    
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError('Invalid path')
    
    if not name:
        name = 'export'

    file = name + file_type

    file_name = file_path / file

    manager = ExportManager(file_name, file_type)

    if data:
        headers: list = data.get('headers')
        entries: list = data.get('entries')

    if file_type == '.csv':
        manager.export_to_csv(entries, headers)
    elif file_type == '.xlsx':
        manager.export_to_excel(entries, headers)
    elif file_type == '.pdf':
        manager.export_to_pdf(entries, headers)