import queue
import sys
import threading

import dialogs
import downloader
import server
import sessionpool
import utils

# TODO: These are broken. Figure out a way to make them work.
EXIT_COMMANDS = ['bye', 'exit', 'kill', 'quit']
MESSAGE_FORMAT = (
    'Size: %s MB\n'
    'Time elapsed: %dm %ds\n'
    'Average download speed: %.2f MB/s')
KB = 1024
MB = 1024*KB

ip_addresses = utils.get_ip_addresses()
session_pool = sessionpool.SessionPool(ip_addresses)

message_queue = queue.Queue()


def listen():
    while True:
        user_input = input()
        if user_input.lower() in EXIT_COMMANDS:
            message_queue.put((sys.exit,))
            sys.exit()
        threading.Thread(target=start, args=(user_input,)).start()


def start(url, path=None):
    if path is None:
        try:
            url, path = url.split(' ', 1)
        except ValueError:
            path = ''
    dtask = downloader.DownloadTask(session_pool, url)
    message_queue.put((saveas, dtask, path))


def saveas(dtask, path):
    if not path:
        path = dialogs.saveas_dialog(initialfile=dtask.name)
    if path:
        dtask.path = path
        threading.Thread(target=wait, args=(dtask,)).start()


def wait(dtask):
    dtask.run()
    message_queue.put((complete, dtask))


def complete(dtask):
    mins, secs = divmod(dtask.time_elapsed, 60)
    avg_speed = dtask.size/MB/dtask.time_elapsed
    message = MESSAGE_FORMAT % (dtask.size//MB, mins, secs, avg_speed)
    dialogs.DownloadCompleteDialog(dtask.url, dtask.path, message)


def main():
    threading.Thread(target=server.run, args=(start,)).start()
    threading.Thread(target=listen).start()
    while True:
        callback, *args = message_queue.get()
        callback(*args)


if __name__ == '__main__':
    main()
