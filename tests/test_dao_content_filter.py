import pytest
import os
import mock
from tempfile import mkstemp
from mib.dao.content_filter import ContentFilter

class TestContenteFilter:

    def test_unsafe_words(self):
        dirname = 'mib/static/txt/'
        tfd, fullpath = mkstemp(dir=dirname, suffix='.txt')
        filename = os.path.basename(fullpath)
        with os.fdopen(tfd, 'w') as temp:
            temp.write('unsafe1\nunsafe2\nunsafe3')

        with mock.patch('os.path.join') as m:
            m.return_value = dirname + filename
            assert ContentFilter.unsafe_words() == ['unsafe1', 'unsafe2', 'unsafe3']
            # the call is repeated to test the caching of the list
            assert ContentFilter.unsafe_words() == ['unsafe1', 'unsafe2', 'unsafe3']
        os.remove(fullpath)

    @pytest.mark.parametrize("body,result", [
        ('unsafe1', True),
        ('unSAfe1', True),
        ('unsafe1 unsafe3', True),
        ('unsafe2 safe', True),
        ('safe unsafe2', True),
        (' unsafe1', True),
        ('unsafe1 ', True),
        ('unsafe safe', False),
        ('un safe1 ', False),
        ('unsafe1unsafe2unsafe3', False),
    ])
    def test_fileter_content(self, body, result):
        with mock.patch('mib.dao.content_filter.ContentFilter.unsafe_words') as m:
            m.return_value = ['unsafe1', 'unsafe2', 'unsafe3']
            assert ContentFilter.filter_content(body) == result


