import os
import tempfile
import unittest

import lxml.html

import memo


def extract_content_of_id(data, node_id):
    html = lxml.html.fromstring(data)
    ns = html.xpath('//*[@id="%s"]' % node_id)
    assert len(ns) == 1
    return ns[0].text_content()


class MemoTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, memo.DATABASE = tempfile.mkstemp()
        with memo.app.app_context():
            memo.init_db()
        memo.app.testing = True
        self.app = memo.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(memo.DATABASE)

    def test_no_entry(self):
        rv = self.app.get('/')
        self.assertIn(b'database initialized', rv.data)

    def test_add_entries(self):
        rv = self.app.get('/')
        self.assertNotIn('a &gt; b', extract_content_of_id(rv.data, 'items'))
        self.assertNotIn('foo', extract_content_of_id(rv.data, 'items'))
        rv = self.app.post('/add', data=dict(
            item="a > b"
        ), follow_redirects=True)
        self.assertIn('a > b', extract_content_of_id(rv.data, 'items'))
        self.assertNotIn('foo', extract_content_of_id(rv.data, 'items'))
        rv = self.app.post('/add', data=dict(
            item="foo"
        ), follow_redirects=True)
        self.assertIn('a > b', extract_content_of_id(rv.data, 'items'))
        self.assertIn('foo', extract_content_of_id(rv.data, 'items'))

    def test_filter_entries(self):
        rv = self.app.post('/add', data=dict(
            item="a > b"
        ), follow_redirects=True)
        rv = self.app.post('/add', data=dict(
            item="foo"
        ), follow_redirects=True)
        rv = self.app.post('/filter', data=dict(
            filter="foo"
        ), follow_redirects=True)
        self.assertNotIn('a > b', extract_content_of_id(rv.data, 'items'))
        self.assertIn(b'foo', rv.data)
        rv = self.app.post('/filter', data=dict(
            filter="b"
        ), follow_redirects=True)
        self.assertIn('a > b', extract_content_of_id(rv.data, 'items'))
        self.assertNotIn('foo', extract_content_of_id(rv.data, 'items'))

    # @unittest.expectedFailure
    def test_filter_entries_buggy(self):
        rv = self.app.post('/add', data=dict(
            item="a > b"
        ), follow_redirects=True)
        rv = self.app.post('/filter', data=dict(
            filter="a > b"
        ), follow_redirects=True)
        self.assertIn('a > b', extract_content_of_id(rv.data, 'items'))


if __name__ == '__main__':
    unittest.main()
