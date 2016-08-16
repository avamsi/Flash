import argparse
import queue
import shlex
import sys
import threading

import dialogs
import downloader
import sessionpool
import utils

EXIT_COMMANDS = ['bye', 'exit', 'kill', 'quit']
MESSAGE_FORMAT = (
    'Size: %s MB\n'
    'Time elapsed: %dm %ds\n'
    'Average download speed: %.2f MB/s')

parser = argparse.ArgumentParser()
parser.add_argument('url')
parser.add_argument('-o', '--out', default=None)

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


def start(user_input):
    args = parser.parse_args(shlex.split(user_input))
    dtask = downloader.DownloadTask(session_pool, args.url, args.out)
    message_queue.put((saveas, dtask))


def saveas(dtask):
    dtask.path = dialogs.save_as_dialog(initialfile=dtask.name)
    threading.Thread(target=wait, args=(dtask,)).start()


def wait(dtask):
    dtask.run()
    message_queue.put((complete, dtask))


def complete(dtask):
    mins, secs = divmod(dtask.time_elapsed, 60)
    avg_speed = dtask.size/2**20/dtask.time_elapsed
    message = MESSAGE_FORMAT % (dtask.size//2**20, mins, secs, avg_speed)
    dialogs.DownloadCompleteDialog(dtask.url, dtask.path, message)


def main():
    threading.Thread(target=listen).start()
    while True:
        callback, *args = message_queue.get()
        callback(*args)


if __name__ == '__main__':
    main()
