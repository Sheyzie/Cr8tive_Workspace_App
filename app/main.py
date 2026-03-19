import logging
from configs.app_config import BASE_DIR
from backend.commands import process_commands
import sys


# logger setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "logs/app.log"),
        # logging.StreamHandler() # to log to console
    ]
)

# sys.argv[main.py, run, command] -> to run backend / test
# sys.argv[main.py, show, command] -> to show logs

if __name__ == '__main__':
    process_commands(sys.argv)