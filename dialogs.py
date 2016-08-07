from functools import partial
from os import startfile
from os.path import dirname
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename

root = Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()
save_as_dialog = partial(asksaveasfilename, parent=root)


class DownloadCompleteDialog(object):

    def __init__(self, url=None, path=None, message=None):
        self._dialog = Toplevel()
        self._url = url
        self._path = path
        self._message = message
        self._set_properties()
        self._add_url()
        self._add_path()
        self._add_message()
        self._add_buttons()
        self._show()

    def _set_properties(self):
        self._dialog.geometry('512x256+700+300')
        self._dialog.title('Download completed')
        self._dialog.resizable(0, 0)
        self._dialog.bind('<Escape>', self._close)

    def _add_url(self):
        url = LabelFrame(self._dialog, text='URL')
        url.pack(fill=X, padx=10, pady=5)
        Label(url, text=self._url).pack(side=LEFT)

    def _add_path(self):
        path = LabelFrame(self._dialog, text='Path')
        path.pack(fill=X, padx=10, pady=5)
        Label(path, text=self._path).pack(side=LEFT)

    def _add_message(self):
        message = Frame(self._dialog)
        message.pack(fill=X, padx=5, pady=5)
        Message(message, text=self._message, width=10**6).pack(side=LEFT)

    def _add_buttons(self):
        buttons = Frame(self._dialog)
        buttons.pack(fill=X, pady=10)

        open_button = Button(buttons, text='Open', command=self._open)
        open_button.pack(ipadx=10, padx=10, side=LEFT)

        open_folder_button = Button(
            buttons, text='Open folder', command=self._open_folder)
        open_folder_button.pack(ipadx=10, padx=10, side=LEFT)

        close_button = Button(buttons, text='Close', command=self._close)
        close_button.pack(ipadx=10, padx=10, side=RIGHT)

    def _open(self):
        startfile(self._path)
        self._close()

    def _open_folder(self):
        startfile(dirname(self._path))
        self._close()

    def _close(self, event=None):
        self._dialog.destroy()

    def _show(self):
        self._dialog.wm_attributes('-topmost', 1)
        self._dialog.focus_force()
        self._dialog.wait_window()
