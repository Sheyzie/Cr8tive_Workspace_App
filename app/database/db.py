import inspect
import sqlite3
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification
from exceptions.exception import ValidationError
from configs import db_config


class DB:

    def __init__(self, using=None):
        log_to_file('Database','Init', 'Initializing connection')
        conn = None
        if not using:
            log_error_to_file('Database', 'Error', f"No Database provided. Ensure DB config is set @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_to_file('Database', 'Error', f"No Database provided. Ensure DB config is set @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            raise ValidationError('No Database provided. Ensure DB config is set')
        try:
            self._db = using + '.db'
            conn = sqlite3.connect(self._db)
            conn.execute("PRAGMA foreign_keys = ON")
            log_to_file('Database','Init', 'Connection completed')
            conn.close()
            self.create_tables()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            if conn:
                conn.close()
            Notification.send_notification(err)
            return
                
    def _connect_to_db(self):
        try:
            self.conn = sqlite3.connect(self._db)

            # access column by name (like a dictionary)
            # self.conn.row_factory = sqlite3.Row

            self.conn.execute("PRAGMA foreign_keys = ON")
            log_to_file('Database','Connect', 'Connection established')
            return self.conn
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error connecting to {self._db} @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error connecting to DB')
            Notification.send_notification(err)
            self.conn = None
            return None
            

    def create_tables(self):
        self._connect_to_db()
        if self.conn:
            self._create_client_table()
            self._create_plan_table()
            self._create_payment_table()
            self._create_subscription_table()
            self._create_visit_table()
            self._create_assigned_client_table()
            self.conn.close()

    def _create_client_table(self):
        log_to_file('Database', 'Init', 'Initializing client table')
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
                        created_at TEXT NOT NULL 
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error creating client table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating client table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)

    def _create_plan_table(self):
        log_to_file('Database', 'Init', 'Initializing plan table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS plan (
                        plan_id TEXT PRIMARY KEY,
                        plan_name TEXT NOT NULL,
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
            log_error_to_file('Database', 'Error', f"Error creating plan table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating plan table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)


    def _create_payment_table(self):
        log_to_file('Database', 'Init', 'Initializing payment table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payment (
                        payment_id TEXT PRIMARY KEY,
                        discount INTEGER NOT NULL,
                        tax INTEGER NOT NULL,
                        total_price INTEGER NOT NULL,
                        amount_paid INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error creating payment table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating payment table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)

    def _create_subscription_table(self):
        log_to_file('Database', 'Init', 'Initializing subscription table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS subscription (
                        subscription_id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        payment_id TEXT NOT NULL,
                        plan_unit INTEGER NOT NULL,
                        expiration_date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (plan_id) REFERENCES plan(plan_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error creating subscription table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating subscription table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)

    def _create_visit_table(self):
        log_to_file('Database', 'Init', 'Initializing visit table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visit (
                        subscription_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error creating visit table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating visit table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)

    def _create_assigned_client_table(self):
        log_to_file('Database', 'Init', 'Initializing assigned_client table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS assigned_client (
                        subscription_id TEXT NOT NULL,
                        client_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION
                        FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f"Error creating assigned_client table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f"Error creating assigned_client table @ {__name__} 'line {inspect.currentframe().f_lineno}'")
            Notification.send_notification(err)

    def save_to_db(self):
        self.conn.commit()

    def drop_db(self):
        from pathlib import Path
        print(f'Dropping database {self._db}...')
        db_file = Path(self._db)
        
        if db_file.exists():
            db_file.unlink()
            print("Database dropped.")
        else:
            print("Database not found.")


class InitDB(DB):
    def __init__(self, using=None):
        if not using:
            using = db_config.DB_NAME
        super().__init__(using)