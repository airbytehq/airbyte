import unittest
import mock
import time
import json

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from analytics.consumer import Consumer, MAX_MSG_SIZE
from analytics.request import APIError


class TestConsumer(unittest.TestCase):

    def test_next(self):
        q = Queue()
        consumer = Consumer(q, '')
        q.put(1)
        next = consumer.next()
        self.assertEqual(next, [1])

    def test_next_limit(self):
        q = Queue()
        upload_size = 50
        consumer = Consumer(q, '', upload_size)
        for i in range(10000):
            q.put(i)
        next = consumer.next()
        self.assertEqual(next, list(range(upload_size)))

    def test_dropping_oversize_msg(self):
        q = Queue()
        consumer = Consumer(q, '')
        oversize_msg = {'m': 'x' * MAX_MSG_SIZE}
        q.put(oversize_msg)
        next = consumer.next()
        self.assertEqual(next, [])
        self.assertTrue(q.empty())

    def test_upload(self):
        q = Queue()
        consumer = Consumer(q, 'testsecret')
        track = {
            'type': 'track',
            'event': 'python event',
            'userId': 'userId'
        }
        q.put(track)
        success = consumer.upload()
        self.assertTrue(success)

    def test_upload_interval(self):
        # Put _n_ items in the queue, pausing a little bit more than
        # _upload_interval_ after each one.
        # The consumer should upload _n_ times.
        q = Queue()
        upload_interval = 0.3
        consumer = Consumer(q, 'testsecret', upload_size=10,
                            upload_interval=upload_interval)
        with mock.patch('analytics.consumer.post') as mock_post:
            consumer.start()
            for i in range(0, 3):
                track = {
                    'type': 'track',
                    'event': 'python event %d' % i,
                    'userId': 'userId'
                }
                q.put(track)
                time.sleep(upload_interval * 1.1)
            self.assertEqual(mock_post.call_count, 3)

    def test_multiple_uploads_per_interval(self):
        # Put _upload_size*2_ items in the queue at once, then pause for
        # _upload_interval_. The consumer should upload 2 times.
        q = Queue()
        upload_interval = 0.5
        upload_size = 10
        consumer = Consumer(q, 'testsecret', upload_size=upload_size,
                            upload_interval=upload_interval)
        with mock.patch('analytics.consumer.post') as mock_post:
            consumer.start()
            for i in range(0, upload_size * 2):
                track = {
                    'type': 'track',
                    'event': 'python event %d' % i,
                    'userId': 'userId'
                }
                q.put(track)
            time.sleep(upload_interval * 1.1)
            self.assertEqual(mock_post.call_count, 2)

    @classmethod
    def test_request(cls):
        consumer = Consumer(None, 'testsecret')
        track = {
            'type': 'track',
            'event': 'python event',
            'userId': 'userId'
        }
        consumer.request([track])

    def _test_request_retry(self, consumer,
                            expected_exception, exception_count):

        def mock_post(*args, **kwargs):
            mock_post.call_count += 1
            if mock_post.call_count <= exception_count:
                raise expected_exception
        mock_post.call_count = 0

        with mock.patch('analytics.consumer.post',
                        mock.Mock(side_effect=mock_post)):
            track = {
                'type': 'track',
                'event': 'python event',
                'userId': 'userId'
            }
            # request() should succeed if the number of exceptions raised is
            # less than the retries paramater.
            if exception_count <= consumer.retries:
                consumer.request([track])
            else:
                # if exceptions are raised more times than the retries
                # parameter, we expect the exception to be returned to
                # the caller.
                try:
                    consumer.request([track])
                except type(expected_exception) as exc:
                    self.assertEqual(exc, expected_exception)
                else:
                    self.fail(
                        "request() should raise an exception if still failing "
                        "after %d retries" % consumer.retries)

    def test_request_retry(self):
        # we should retry on general errors
        consumer = Consumer(None, 'testsecret')
        self._test_request_retry(consumer, Exception('generic exception'), 2)

        # we should retry on server errors
        consumer = Consumer(None, 'testsecret')
        self._test_request_retry(consumer, APIError(
            500, 'code', 'Internal Server Error'), 2)

        # we should retry on HTTP 429 errors
        consumer = Consumer(None, 'testsecret')
        self._test_request_retry(consumer, APIError(
            429, 'code', 'Too Many Requests'), 2)

        # we should NOT retry on other client errors
        consumer = Consumer(None, 'testsecret')
        api_error = APIError(400, 'code', 'Client Errors')
        try:
            self._test_request_retry(consumer, api_error, 1)
        except APIError:
            pass
        else:
            self.fail('request() should not retry on client errors')

        # test for number of exceptions raise > retries value
        consumer = Consumer(None, 'testsecret', retries=3)
        self._test_request_retry(consumer, APIError(
            500, 'code', 'Internal Server Error'), 3)

    def test_pause(self):
        consumer = Consumer(None, 'testsecret')
        consumer.pause()
        self.assertFalse(consumer.running)

    def test_max_batch_size(self):
        q = Queue()
        consumer = Consumer(
            q, 'testsecret', upload_size=100000, upload_interval=3)
        track = {
            'type': 'track',
            'event': 'python event',
            'userId': 'userId'
        }
        msg_size = len(json.dumps(track).encode())
        # number of messages in a maximum-size batch
        n_msgs = int(475000 / msg_size)

        def mock_post_fn(_, data, **kwargs):
            res = mock.Mock()
            res.status_code = 200
            self.assertTrue(len(data.encode()) < 500000,
                            'batch size (%d) exceeds 500KB limit'
                            % len(data.encode()))
            return res

        with mock.patch('analytics.request._session.post',
                        side_effect=mock_post_fn) as mock_post:
            consumer.start()
            for _ in range(0, n_msgs + 2):
                q.put(track)
            q.join()
            self.assertEqual(mock_post.call_count, 2)

    @classmethod
    def test_proxies(cls):
        consumer = Consumer(None, 'testsecret', proxies='203.243.63.16:80')
        track = {
            'type': 'track',
            'event': 'python event',
            'userId': 'userId'
        }
        consumer.request([track])
