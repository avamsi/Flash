import contextlib
import logging
import queue
import time

import requests
import requests_toolbelt

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s [%(asctime)s]')
logging.getLogger('requests').setLevel(logging.WARNING)


class SessionPool(object):

    def __init__(self, ip_addresses=None):
        self._sessions = queue.Queue()
        self._size = 0
        if ip_addresses is not None:
            self.update(ip_addresses)

    @property
    def size(self):
        return self._size

    def update(self, ip_addresses):
        for ip_address in ip_addresses:
            self.add(ip_address)
        logging.info('%s IP addresses addded to pool', len(ip_addresses))

    def add(self, ip_address):
        self._sessions.put(self._source_address_session(ip_address))
        self._size += 1

    @staticmethod
    def _source_address_session(ip_address):
        session = requests.Session()
        session.headers.update({'accept-encoding': 'identity'})
        adapter = requests_toolbelt.SourceAddressAdapter(ip_address)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @contextlib.contextmanager
    def _session(self):
        session = self._sessions.get()
        try:
            yield session
        except requests.ConnectionError:
            time.sleep(5)
        except requests.Timeout as e:
            logging.info('request timed out, %s', type(e).__name__)
        finally:
            self._sessions.put(session)

    def request(self, method, url, **kwargs):
        while True:
            with self._session() as session:
                return session.request(method, url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('HEAD', url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    @staticmethod
    def _check_header_conflicts(kwargs):
        try:
            kwargs['headers']['range']
        except KeyError:
            pass
        else:
            raise ValueError('range must not be specified when using stream')

    def _stream(self, url, begin, end, chunk_size, **kwargs):
        kwargs.setdefault('headers', {})['range'] = 'bytes=%s-%s' % (begin, end)
        with self._session() as session:
            response = session.get(url, stream=True, **kwargs)
            yield from response.iter_content(chunk_size)

    def stream(self, url, begin, end, chunk_size, **kwargs):
        self._check_header_conflicts(kwargs)
        while begin <= end:
            for chunk in self._stream(url, begin, end, chunk_size, **kwargs):
                assert len(chunk) == chunk_size or begin + len(chunk) == end + 1
                yield chunk
                begin += chunk_size
