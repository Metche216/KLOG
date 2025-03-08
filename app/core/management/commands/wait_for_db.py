"""
Django command to wait for the db to be available
"""
import time 

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A django command to wait for the db to be loaded"""
    def handle(self, *args, **options):
        """Entrypoint for command"""
        self.stdout.write('Waitigin for database...')
        db_up = False
        while db_up is False:
            try: 
                self.check(databases=['default'])
            except:
                time.sleep(1)
        