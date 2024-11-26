from datetime import date, datetime, timedelta
from decimal import Decimal
import unittest

from dateutil.tz import tzutc
import six

from analytics import utils


class TestUtils(unittest.TestCase):

    def test_timezone_utils(self):
        now = datetime.now()
        utcnow = datetime.now(tz=tzutc())
        self.assertTrue(utils.is_naive(now))
        self.assertFalse(utils.is_naive(utcnow))

        fixed = utils.guess_timezone(now)
        self.assertFalse(utils.is_naive(fixed))

        shouldnt_be_edited = utils.guess_timezone(utcnow)
        self.assertEqual(utcnow, shouldnt_be_edited)

    def test_clean(self):
        simple = {
            'decimal': Decimal('0.142857'),
            'unicode': six.u('woo'),
            'date': datetime.now(),
            'long': 200000000,
            'integer': 1,
            'float': 2.0,
            'bool': True,
            'str': 'woo',
            'none': None
        }

        complicated = {
            'exception': Exception('This should show up'),
            'timedelta': timedelta(microseconds=20),
            'list': [1, 2, 3]
        }

        combined = dict(simple.items())
        combined.update(complicated.items())

        pre_clean_keys = combined.keys()

        utils.clean(combined)
        self.assertEqual(combined.keys(), pre_clean_keys)

    def test_clean_with_dates(self):
        dict_with_dates = {
            'birthdate': date(1980, 1, 1),
            'registration': datetime.utcnow(),
        }
        self.assertEqual(dict_with_dates, utils.clean(dict_with_dates))

    @classmethod
    def test_bytes(cls):
        if six.PY3:
            item = bytes(10)
        else:
            item = bytearray(10)

        utils.clean(item)

    def test_clean_fn(self):
        cleaned = utils.clean({'fn': lambda x: x, 'number': 4})
        self.assertEqual(cleaned['number'], 4)
        if 'fn' in cleaned:
            self.assertEqual(cleaned['fn'], None)

    def test_remove_slash(self):
        self.assertEqual('http://segment.io',
                         utils.remove_trailing_slash('http://segment.io/'))
        self.assertEqual('http://segment.io',
                         utils.remove_trailing_slash('http://segment.io'))
