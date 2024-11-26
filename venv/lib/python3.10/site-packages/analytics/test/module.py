import unittest

import analytics


class TestModule(unittest.TestCase):

    # def failed(self):
    #     self.failed = True

    def setUp(self):
        self.failed = False
        analytics.write_key = 'testsecret'
        analytics.on_error = self.failed

    def test_no_write_key(self):
        analytics.write_key = None
        self.assertRaises(Exception, analytics.track)

    def test_no_host(self):
        analytics.host = None
        self.assertRaises(Exception, analytics.track)

    def test_track(self):
        analytics.track('userId', 'python module event')
        analytics.flush()

    def test_identify(self):
        analytics.identify('userId', {'email': 'user@email.com'})
        analytics.flush()

    def test_group(self):
        analytics.group('userId', 'groupId')
        analytics.flush()

    def test_alias(self):
        analytics.alias('previousId', 'userId')
        analytics.flush()

    def test_page(self):
        analytics.page('userId')
        analytics.flush()

    def test_screen(self):
        analytics.screen('userId')
        analytics.flush()

    def test_flush(self):
        analytics.flush()
