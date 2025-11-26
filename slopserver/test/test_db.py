from slopserver.db import *
from slopserver.models import *
from slopserver.settings import settings
from sqlalchemy import create_engine
import unittest

class TestDBFuncs(unittest.TestCase):

    test_db_url = settings.db_url
    engine = None

    def setUp(self):
        engine = create_engine(self.test_db_url)

    