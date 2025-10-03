from datetime import datetime

# log data into log
log_file: str = 'logs.log'
error_log: str = 'error_logs.log'

def log_to_file(sender: str, log_type: str, log: str) -> None:
    entry: str = f'{datetime.now()}-{sender.upper()}-[{log_type.upper()}]-{log}\n'
    with open(log_file, 'a') as file:
        file.write(entry)

def log_error_to_file(sender: str, log_type: str, log: str) -> None:
    entry: str = f'{datetime.now()}-{sender.upper()}-[{log_type.upper()}]-{log}\n'
    with open(log_file, 'a') as file:
        file.write(entry)