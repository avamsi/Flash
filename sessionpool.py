import logging
import queue
import time

import requests
import requests_toolbelt

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)


class SessionPool(object):

    def __init__(self, ip_addresses=None):
        self.sessions = queue.Queue()
        self.size = 0
        if ip_addresses is not None:
            self.update(ip_addresses)

    def update(self, ip_addresses):
        for ip_address in ip_addresses:
            self.add(ip_address)
        logging.info('%s IP addresses addded to pool', len(ip_addresses))

    def add(self, ip_address):
        self.sessions.put(self._source_address_session(ip_address))
        self.size += 1

    @staticmethod
    def _source_address_session(ip_address):
        session = requests.Session()
        adapter = requests_toolbelt.SourceAddressAdapter(ip_address)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _request(self, method, url, **kwargs):
        while True:
            session = self.sessions.get()
            try:
                return session.request(method, url, **kwargs)
            except requests.ConnectionError as e:
                time.sleep(5)
            except requests.Timeout as e:
                logging.info('request timed out, %s', type(e).__name__)
            finally:
                self.sessions.put(session)

    def head(self, url, **kwargs):
        return self._request('head', url, **kwargs)

    def get(self, url, **kwargs):
        return self._request('get', url, **kwargs)
