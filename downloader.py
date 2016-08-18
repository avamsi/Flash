import cgi
import logging
import os.path
import posixpath
import re
import shutil
import threading
import time
import tempfile
import urllib.parse
import queue

import experimental

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s [%(asctime)s]')

KB = 1024
MB = 1024*KB


class DownloadTask(object):

    MIN_CHUNK_SIZE = 100*KB
    MAX_CHECKS_FOR_FILE_NAME = 10**6
    PARTS_PER_IP = 8
    TIMEOUT = 25

    def __init__(self, session_pool, url, name=None):
        self.pool = session_pool
        self.url = url
        self.name = name
        self.update_info()
        self.chunks = []
        self.done_queue = queue.Queue()
        self._path = None  # ask user for path.

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = os.path.normpath(path)

    def update_info(self):
        response = self.pool.head(self.url, allow_redirects=True)
        if self.name is None:
            try:
                _, params = cgi.parse_header(response.headers['content-disposition'])
                try:
                    self.name = params['filename*'][7:]
                except KeyError:
                    self.name = params['filename']
            except KeyError:
                path = urllib.parse.urlparse(self.url).path
                self.name = posixpath.basename(path)

        self.name = urllib.parse.unquote(self.name)
        self.name = re.sub(r'[\\/:*?"<>|]', '_', self.name)  # quick fix for Windows.
        self.size = int(response.headers['content-length'])
        logging.info('%s | %s MB', self.name, self.size//MB)

    def run(self):
        if not self._path or self._path is None:
            self._path = os.path.abspath(self.name)
        logging.info('Downloading to %s', self._path)
        self.start_time = time.monotonic()
        self.temp_directory = tempfile.mkdtemp()
        logging.info('Created a temp directory at %s', self.temp_directory)
        self.start_workers()

    def start_workers(self):
        chunk_size = max(self.MIN_CHUNK_SIZE, self.size//(self.PARTS_PER_IP*self.pool.size))
        threads = []
        begin = 0
        while begin <= self.size:
            end = min(begin + chunk_size, self.size) - 1
            byte_range = 'bytes=%s-%s' % (begin, end)
            chunk_path = os.path.join(self.temp_directory, str(begin))
            self.chunks.append(chunk_path)
            begin += chunk_size
            t = threading.Thread(target=self.worker, args=(chunk_path, byte_range))
            threads.append(t)
            t.start()
        self.wait(threads)

    def worker(self, chunk_path, byte_range):
        headers = {'range': byte_range}
        data = self.pool.get(self.url, timeout=self.TIMEOUT, headers=headers).content
        with open(chunk_path, 'wb') as chunk:
            chunk.write(data)
        self.done_queue.put(None)

    def wait(self, threads):
        threading.Thread(target=self.progress, args=(len(threads),)).start()
        for t in threads:
            t.join()
        self.cleanup()

    def progress(self, parts):
        dialog = experimental.progress_dialog_async(
            self.name, parts, self.url, self._path)
        i = 1
        while i <= parts:
            self.done_queue.get()
            dialog.progress = i
            i += 1

    def cleanup(self):
        self.update_path()
        with open(self._path, 'wb') as out:
            for chunk_path in self.chunks:
                with open(chunk_path, 'rb') as chunk:
                    out.write(chunk.read())
        logging.info('File saved as %s', self._path)
        shutil.rmtree(self.temp_directory)
        self.time_elapsed = time.monotonic() - self.start_time

    def update_path(self):
        if os.path.exists(self._path):
            path_wo_ext, ext = os.path.splitext(self._path)
            for i in range(self.MAX_CHECKS_FOR_FILE_NAME):
                tmp_path_wo_ext = path_wo_ext + ('_%s' % i)
                tmp_path = tmp_path_wo_ext + ext
                if not os.path.exists(tmp_path):
                    self._path = tmp_path
                    return
