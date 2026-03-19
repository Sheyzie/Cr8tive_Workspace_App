import inspect
import sqlite3
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification
from exceptions.exception import ValidationError
from configs import db_config
from pathlib import Path
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DB:

    stdout = sys.stdout
    stderr = sys.stderr
    _db = None

    def __init__(self, using):
        logger.info('Initializing database connection...')
        self.stdout.write('\r\nInitializing database connection...\n')
        self.stdout.flush()
        Notification.send_notification('\nInitializing database connection...')

        # self.stdout = sys.stdout
        # self.stderr = sys.stderr

        conn = None
        if not using:
            logger.warn(f"No Database provided. Ensure DB config is set @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            self.stderr.write('No Database provided. Ensure DB config is set')
            self.stderr.flush()
            exit(1)
        try:
            self._db = using
            conn = sqlite3.connect(Path(self._db))
            conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f'Database connection established to {self._db}')
            Notification.send_notification('Database connection established')
            conn.close()

            self._init_database_tables()
        except Exception as err:
            logger.exception(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()
    
            if conn:
                conn.close()
            Notification.send_notification(err)
            return
                
    def _connect_to_db(self):
        if self._db is None:
            DB.set_db_name()
        try:
            self.stdout.write('\r\nInitializing database connection...\n')
            self.conn = sqlite3.connect(Path(self._db))

            # access column by name (like a dictionary)
            # self.conn.row_factory = sqlite3.Row

            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info('Database connection established')
            self.stdout.write('Database connection established\n')
            self.stdout.flush()
            return self.conn
        except Exception as err:
            logger.exception(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err) + '\n')
            self.stderr.flush()
            Notification.send_notification(err)
            self.conn = None
            exit(1)

    @classmethod
    def set_db_name(cls):
        is_test_environ = os.getenv('CURRENT_WORKING_DB_ENVIRON', '').lower() == 'test' 
        using = db_config.TEST_DB_NAME
        if not is_test_environ:
            using = db_config.DB_NAME

        if not using:
            logger.warn(f"Database name not found\n")
            cls.stderr.write(f"Database name not set found\n")
            cls.stderr.flush()
            exit(0)

        cls._db = using
        return using

    def _init_database_tables(self):
        tables = [
            'client', 'plan', 'payment', 
            'subscription', 'visit', 'assigned_client'
        ]

        for table_name in tables:
            exists = self._check_if_table_exist(table_name)
            
            if exists:
                self.stdout.write(f'\r\n{table_name} table exist\n')
                self.stdout.flush()
            else:
                self.create_tables(table_name)

    def create_tables(self, table_name):
        self._connect_to_db()
        if self.conn:
            self.stdout.write(f'\r\nCreating database table {table_name}...')
            self.stdout.flush()
            match table_name:
                case 'client':   
                    self._create_client_table()
                case 'plan':
                    self._create_plan_table()
                case 'subscription':
                    self._create_subscription_table()
                case 'payment':
                    self._create_payment_table()
                case 'visit':
                    self._create_visit_table()
                case 'assigned_client':
                    self._create_assigned_client_table()
                case _:
                    self.stdout.write(f'Unknown table name: {table_name}')
                    self.stdout.flush()
                    self.conn.close()

            self.conn.close()

        # self.stdout.write('\nTable initialization complete\n')
        # self.stdout.flush()
        
    def _check_if_table_exist(self, table_name: str):
        self._connect_to_db()
        if self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))

                result = cursor.fetchone()
                return result

            except Exception as err:
                self.stderr.write(f"Error creating client table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
                self.stderr.write(str(err))
                self.stderr.flush()


    def _create_client_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS client (
                        client_id TEXT PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        company_name TEXT,
                        email TEXT,
                        phone TEXT NOT NULL UNIQUE,
                        display_name TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating client table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def _create_plan_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS plan (
                        plan_id TEXT PRIMARY KEY,
                        plan_name TEXT NOT NULL UNIQUE,
                        duration INTEGER NOT NULL,
                        plan_type TEXT NOT NULL,
                        slot INTEGER NOT NULL,
                        guest_pass INTEGER NOT NULL,
                        price INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating plan table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def _create_subscription_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS subscription (
                        subscription_id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        plan_unit INTEGER NOT NULL,
                        expiration_date TEXT NOT NULL,
                        discount INTEGER NOT NULL,
                        discount_type TEXT NOT NULL,
                        vat INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        payment_status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (plan_id) REFERENCES plan(plan_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating subscription table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def _create_payment_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payment (
                        payment_id TEXT PRIMARY KEY,
                        client_id TEXT NOT NULL,
                        subscription_id TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating payment table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def _create_visit_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visit (
                        visit_id TEXT PRIMARY KEY,
                        subscription_id TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating visit table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def _create_assigned_client_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS assigned_client (
                        subscription_id TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            self.stderr.write(f"Error creating visit table @ {__name__} 'line {inspect.currentframe().f_lineno}'\n")
            self.stderr.write(str(err))
            self.stderr.flush()

    def save_to_db(self):
        self.conn.commit()

    def drop_db(self):
        self.stdout.write(f'Dropping database {self._db}\n')
        self.stdout.flush()
        db_file = Path(self._db)
        
        if db_file.exists():
            db_file.unlink()
            self.stdout.write(f'Dropped {self._db} database successfully\n')
            self.stdout.flush()

        else:
            self.stdout.write(f'Database {self._db} not found\n')
            self.stdout.flush()
            exit(1)


class InitDB(DB):
    def __init__(self):
        is_test_environ = os.getenv('CURRENT_WORKING_DB_ENVIRON', '').lower() == 'test' 
        using = db_config.TEST_DB_NAME
        if not is_test_environ:
            using = db_config.DB_NAME

        super().__init__(using)