import time

from django.db import connection
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
import pyodbc

class Command(BaseCommand):
    """Django command that waits for database to be available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Connecting to the database...')
        # server = 'TTL-5NJJYY2\SQLEXPRESS'
        # database = 'gsicosttool'
        # username = 'gsicostoolweb'
        # password = 'fed434$2!!11'
        # cnxn = pyodbc.connect(
        #     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        # cursor = cnxn.cursor()


        db_conn = None
        while not db_conn:
            try:
                connection.ensure_connection()
                db_conn = True
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
