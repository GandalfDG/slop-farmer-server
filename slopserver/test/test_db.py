from slopserver.db import *
from slopserver.models import *
from slopserver.settings import settings
from sqlalchemy import create_engine
import unittest

class TestDBFuncs(unittest.TestCase):

    test_db_url = settings.db_url

    def setUp(self):
        self.engine = create_engine(self.test_db_url)

    def test_get_top_offenders(self):
        items = top_offenders(self.engine)
        print(items)
        self.assertEqual(items[0][0], "moogle.com")

