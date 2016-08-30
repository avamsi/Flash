import cgi
import collections
import logging
import os.path
import posixpath
import re
import shutil
import threading
import time
import tempfile
import urllib.parse

import experimental

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s [%(asctime)s]')

KB = 1024
MB = 1024*KB


class DownloadTask(object):

    _MIN_PART_SIZE = 100*KB
    _MAX_CHECKS_FOR_FILE_NAME = 10**5
    _PARTS_PER_IP = 8
    _TIMEOUT = 25

    def __init__(self, session_pool, url):
        self._pool = session_pool
        self._url = url
        self._update_info()
        self._downloaded = 0
        self._downloaded_lock = threading.Lock()
        self._parts = []

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = os.path.normpath(path)

    @property
    def time_elapsed(self):
        return self._time_elapsed

    @property
    def url(self):
        return self._url

    def _update_info(self):
        response = self._pool.head(self._url, allow_redirects=True)
        try:
            _, params = cgi.parse_header(response.headers['content-disposition'])
            try:
                name = params['filename*'][7:]
            except KeyError:
                name = params['filename']
        except KeyError:
            path = urllib.parse.urlparse(self._url).path
            name = posixpath.basename(path)

        name = urllib.parse.unquote(name)
        self._name = re.sub(r'[\\/:*?"<>|]', '_', name)
        self._size = int(response.headers['content-length'])
        logging.info('%s | %s MB', self._name, self._size//MB)

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    def run(self):
        logging.info('Downloading to %s', self._path)
        self._start_time = time.monotonic()
        self._temp_directory = tempfile.mkdtemp()
        logging.info('Created a temp directory at %s', self._temp_directory)
        self._start_workers()

    def _start_workers(self):
        part_size = max(self._MIN_PART_SIZE,
                        self._size // (self._PARTS_PER_IP * self._pool.size))
        threads = []
        begin = 0
        while begin < self._size:
            end = min(begin + part_size, self._size) - 1
            part_path = os.path.join(self._temp_directory, str(begin))
            self._parts.append(part_path)
            t = threading.Thread(target=self._worker, args=(part_path, begin, end))
            begin = end + 1
            threads.append(t)
            t.start()
        self._wait(threads)

    def _worker(self, part_path, begin, end):
        stream = self._pool.stream(self._url, begin, end, KB, timeout=self._TIMEOUT)
        chunks = []
        for chunk in stream:
            chunks.append(chunk)
            with self._downloaded_lock:
                self._downloaded += len(chunk)

        with open(part_path, 'wb') as part:
            part.write(b''.join(chunks))

    def _wait(self, threads):
        threading.Thread(target=self._progress).start()
        for t in threads:
            t.join()
        self._cleanup()

    def _progress(self):
        dialog = experimental.progress_dialog_async(self._name, self._url,
                                                    self._path, self._size)
        last_10_diffs = collections.deque(maxlen=10)
        downloaded_old = 0
        while downloaded_old < self._size:
            downloaded = self._downloaded
            last_10_diffs.append(downloaded - downloaded_old)
            downloaded_old = downloaded
            speed = sum(last_10_diffs)
            if speed != 0:
                time_left = (self._size - downloaded)//speed
                time_left = divmod(time_left, 60)
            else:
                time_left = None
            speed /= MB
            dialog.update(downloaded, speed, time_left)
            time.sleep(.1)

    def _cleanup(self):
        self._update_path()
        with open(self._path, 'wb') as out:
            for part_path in self._parts:
                with open(part_path, 'rb') as part:
                    out.write(part.read())
        logging.info('File saved as %s', self._path)
        shutil.rmtree(self._temp_directory)
        self._time_elapsed = time.monotonic() - self._start_time

    def _update_path(self):
        if os.path.exists(self._path):
            path_wo_ext, ext = os.path.splitext(self._path)
            for i in range(self._MAX_CHECKS_FOR_FILE_NAME):
                tmp_path_wo_ext = path_wo_ext + ('_%s' % i)
                tmp_path = tmp_path_wo_ext + ext
                if not os.path.exists(tmp_path):
                    self._path = tmp_path
                    return
