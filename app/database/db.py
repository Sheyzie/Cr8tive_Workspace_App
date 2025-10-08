import sqlite3
from logs.utils import log_to_file, log_error_to_file
from notification.notification import Notification
from exceptions.exception import ValidationError
from configs import db_config


class InitDB:

    def __init__(self, using=db_config.DB_NAME):
        log_to_file('Database','Init', 'Initializing connection')
        conn = None
        if not using:
            log_error_to_file('Database', 'Error', 'No Database provided. Ensure DB config is set')
            log_to_file('Database', 'Error', 'No Database provided. Ensure DB config is set')
            raise ValidationError('No Database provided. Ensure DB config is set')
        try:
            conn = sqlite3.connect(self._db)
            conn.execute("PRAGMA foreign_keys = ON")
            log_to_file('Database','Init', 'Connection completed')
            conn.close()
        except Exception as err:
            log_error_to_file('Database', 'Error', f'Error connecting to {self._db}: {err}')
            log_to_file('Database', 'Error', f'Error connecting to {self._db}')
            if conn:
                conn.close()
            Notification.send_notification(err)
            return
                
    def _connect_to_db(self):
        try:
            self.conn = sqlite3.connect(self._db)
            self.conn.execute("PRAGMA foreign_keys = ON")
            log_to_file('Database','Connect', 'Connection established')
            return self.conn
        except Exception as err:
            log_error_to_file('Database', 'Error', f'Error connecting to {self._db}: {err}')
            log_to_file('Database', 'Error', f'Error connecting to {self._db}')
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
            log_error_to_file('Database', 'Error', f'Error creating client table')
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error creating client table')
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
                        price INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f'Error creating plan table')
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error creating plan table')
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
            log_error_to_file('Database', 'Error', f'Error creating payment table')
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error creating payment table')
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
                        total_price INTEGER NOT NULL,
                        amount_paid INTEGER NOT NULL,
                        payment_id TEXT NOT NULL,
                        expiration TEXT NOT NULL,
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
            log_error_to_file('Database', 'Error', f'Error creating subscription table')
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error creating subscription table')
            Notification.send_notification(err)

    def _create_visit_table(self):
        log_to_file('Database', 'Init', 'Initializing visit table')
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visit (
                        subscription_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id) ON DELETE CASCADE ON UPDATE NO ACTION
                    );
            ''')
            self.conn.commit()
        except Exception as err:
            log_error_to_file('Database', 'Error', f'Error creating visit table')
            log_error_to_file('Database', 'Error', f'{err}')
            log_to_file('Database', 'Error', f'Error creating visit table')
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
