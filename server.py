import http.server
import logging
import threading
import urllib.parse

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s [%(asctime)s]')

SERVER_ADDRESS = ('localhost', 20456)


def run(target):

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parts = urllib.parse.urlsplit(self.path)
            params = urllib.parse.parse_qs(parts.query)
            url, path = params['url'][0], params['path'][0]
            logging.info('%s %s', url, path)
            threading.Thread(target=target, args=(url, path)).start()
            # TODO: Wrong to send an empty response?

    logging.info('Listening on %s:%s', *SERVER_ADDRESS)
    httpd = http.server.HTTPServer(SERVER_ADDRESS, Handler)
    httpd.serve_forever()
