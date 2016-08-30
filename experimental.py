from threading import Thread
from tkinter import *
from tkinter.ttk import *
from queue import Queue

KB = 1024
MB = 1024*KB


class ProgressDialog(object):

    def __init__(self, name, url, path, size):
        self._dialog = Tk()
        self._title_format = '({}%) ' + name
        self._size = size
        self._set_properties()
        self._add_main()
        self._add_label(url)
        self._add_label(path)
        self._add_table()
        self._add_progress_bar()

    def _set_properties(self):
        self._dialog.geometry('440x220+740+360')
        self._dialog.title(self._title_format.format(0))
        self._dialog.resizable(0, 0)
        self._dialog.bind('<Escape>', self._iconify)
        self._dialog.protocol('WM_DELETE_WINDOW', self._iconify)

    def _add_main(self):
        self._main = Frame(self._dialog)
        self._main.pack(padx=10, pady=10, fill=X)

    def _add_label(self, text):
        label = Label(self._main, text=text)
        label.pack(fill=X)

    def _add_table(self):
        Separator(self._main).pack(pady=5)
        self._add_size_row()
        self._add_downloaded_row()
        self._add_speed_row()
        self._add_time_row()
        Separator(self._main).pack(pady=5)

    def _add_size_row(self):
        self._add_row('Size', '%.2f MB' % (self._size/MB))

    def _add_downloaded_row(self):
        self._downloaded = StringVar(self._main, '0 MB')
        self._add_row('Downloaded', self._downloaded)

    def _add_speed_row(self):
        self._speed = StringVar(self._main, '0 MB/s')
        self._add_row('Speed', self._speed)

    def _add_time_row(self):
        self._time_left = StringVar(self._main, '-')
        self._add_row('Time left', self._time_left)

    def _add_row(self, text, variable):
        row = Frame(self._main)
        row.pack(fill=X)
        Label(row, text=text, width=24, foreground='blue').pack(side=LEFT)
        if isinstance(variable, str):
            Label(row, text=variable).pack(side=LEFT)
        else:
            Label(row, textvariable=variable).pack(side=LEFT)

    def _add_progress_bar(self):
        self._progressbar = Progressbar(self._main, maximum=self._size)
        self._progressbar.pack(fill=X, pady=5)

    def update(self, downloaded, speed, time_left):
        self._progressbar['value'] = downloaded
        self._dialog.title(self._title_format.format(100*downloaded//self._size))
        self._downloaded.set('%.2f MB' % (downloaded/MB))
        self._speed.set('%.2f MB/s' % speed)
        if time_left is not None:
            self._time_left.set('%sm %ss' % time_left)
        else:
            self._time_left.set('-')

    def show(self):
        self._dialog.focus_force()
        self._dialog.after(100, self._poll)
        self._dialog.mainloop()

    def _poll(self):
        if self._progressbar['value'] >= self._size:
            self._dialog.quit()
        self._dialog.after(100, self._poll)

    def _iconify(self, event=None):
        self._dialog.iconify()


def progress_dialog_async(*args, **kwargs):
    progress_dialog_queue = Queue()

    def create_progress_dialog():
        progress_dialog = ProgressDialog(*args, **kwargs)
        progress_dialog_queue.put(progress_dialog)
        progress_dialog.show()

    Thread(target=create_progress_dialog).start()
    return progress_dialog_queue.get()
