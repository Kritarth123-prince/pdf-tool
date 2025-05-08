import os
import logging
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_connection'):
            self.host = os.environ["DB_HOST"]
            self.user = os.environ["DB_USER"]
            self.password = os.environ["DB_PASSWORD"]
            self.database = os.environ["DB_NAME"]

            self._connection = None
            self.connect()
            self.initialize_database()

    def connect(self):
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("Connected to MySQL database")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise

    def initialize_database(self):
        try:
            cursor = self._connection.cursor()
            cursor.execute(f"USE {self.database}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    activity_type VARCHAR(50),
                    activity_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    task VARCHAR(100),
                    input_file_path TEXT,
                    output_file_path TEXT,
                    date_time DATETIME,
                    files_count INT
                )
            """)

            self._connection.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_connection(self):
        if not self._connection.is_connected():
            self.connect()
        return self._connection

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("MySQL connection closed")

    def execute_query(self, query, params=None, fetch_one=False):
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            connection.rollback()
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()

    def authenticate_user(self, username, password):
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            logger.error(f"Error authenticating user: {e}")
            raise

    def log_task(self, username, task_type, input_files, output_file):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        input_files_str = ', '.join(input_files) if isinstance(input_files, list) else input_files
        files_count = len(input_files) if isinstance(input_files, list) else 1

        try:
            self.execute_query("""
                INSERT INTO task_logs (username, task, input_file_path, output_file_path, date_time, files_count)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                username,
                task_type,
                input_files_str,
                output_file,
                timestamp,
                files_count
            ))
        except Exception as e:
            logger.error(f"Task logging failed: {e}")


