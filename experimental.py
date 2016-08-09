from threading import Thread
from tkinter import *
from tkinter.ttk import *
from queue import Queue


class ProgressDialog(object):

    def __init__(self, name, maximum, url, path):
        self._dialog = Tk()
        self._title_format = '({}%) ' + name
        self._max = maximum
        self._url = url
        self._path = path
        self._set_properties()
        self._add_url()
        self._add_path()
        self._add_progress_bar()

    def _set_properties(self):
        self._dialog.geometry('504x222+708+360')
        self._dialog.title(self._title_format.format(0))
        self._dialog.resizable(0, 0)
        # TODO: make this not closeable

    def _add_url(self):
        url = LabelFrame(self._dialog, text='URL')
        url.pack(fill=X, padx=10, pady=10)
        Label(url, text=self._url).pack(side=LEFT)

    def _add_path(self):
        path = LabelFrame(self._dialog, text='Path')
        path.pack(fill=X, padx=10, pady=10)
        Label(path, text=self._path).pack(side=LEFT)

    def _add_progress_bar(self):
        progress = LabelFrame(self._dialog, text='Progress')
        progress.pack(fill=X, padx=10, pady=10)
        self._progressbar = Progressbar(progress, length=480, maximum=self._max)
        self._progressbar.pack(pady=10)

    def _set_progress(self, value):
        self._progressbar['value'] = value
        self._dialog.title(self._title_format.format(100*value//self._max))

    progress = property(fset=_set_progress)

    def show(self):
        self._dialog.focus_force()
        self._dialog.after(100, self._poll)
        self._dialog.mainloop()

    def _poll(self):
        if self._progressbar['value'] >= self._max:
            self._dialog.quit()
        self._dialog.after(100, self._poll)


def progress_dialog_async(*args, **kwargs):
    progress_dialog_queue = Queue()

    def create_progress_dialog():
        progress_dialog = ProgressDialog(*args, **kwargs)
        progress_dialog_queue.put(progress_dialog)
        progress_dialog.show()

    Thread(target=create_progress_dialog).start()
    return progress_dialog_queue.get()
