"""Test django management commands"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psychopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase



@patch('core.management.commands.wait_for_db.Command.check') # the result of that command is going to be passed to the class methods as an argument.
class CommandsTests(SimpleTestCase):
    """Test Commands"""
    
    def test_wait_for_db_ready(self, patched_check):
        """Tests waiting for db if db ready"""
        patched_check.return_value = True
        
        call_command('wait_for_db')
        
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')        
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting operational error"""
        patched_check.side_effect = [Psychopg2Error] * 2 + [OperationalError] * 3 + [True] #raise an error each time the function is called
        
        call_command('wait_for_db')
        
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])