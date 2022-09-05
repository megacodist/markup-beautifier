from pathlib import Path
import PIL.Image
import PIL.ImageTk
import requests
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlparse, urlunparse

from megacodist.html import HtmlTagsChecker

from dialogs import BeautifyingDialog


class AsyncRequest(Thread):
    def __init__(
            self,
            group: None,
            target: Callable[..., Any] | None = ...,
            name: str | None = ...,
            args: Iterable[Any] = ...,
            kwargs: Mapping[str, Any] | None = ...,
            *,
            daemon: bool | None = ...,
            url: str
            ) -> None:

        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.url = url
        self.htmlResponse = None

    def run(self) -> None:
        import platform
        try:
            pltfrm = platform.system_alias(
                platform.system(),
                platform.release(),
                platform.version())
            headers = {
                'User-Agent': (
                    'Mozilla/5.0, '
                    + f'({pltfrm}) '
                    + '(compatible; markup-beautifier; +https://github.com/megacodist/markup-beautifier)')}
            self.htmlResponse = requests.get(
                self.url,
                headers=headers,
                ).text
        except Exception as err:
            self.htmlResponse = str(err)


class BeautifierWindow(tk.Tk):
    # Definning class attributes...
    WRAP_MODES = (
        ('char', 'Character'),
        ('word', 'Word'),
        ('none', 'Line'),
    )

    def __init__(self) -> None:
        super().__init__()
        self.title('Markup Beatifier')

        # Creating address bar frame...
        self.frm_addressbar = ttk.Frame(self)
        self.frm_addressbar.pack(
            side='top',
            fill='x',
            anchor='n',
            expand=0,    # To achieve fixed height
            padx=4,
            pady=(4, 2,)
        )

        #
        # Loading 'start.png'...
        self.img_go = Path(__file__).resolve().parent
        self.img_go = self.img_go / 'res/start.png'
        self.img_go = PIL.Image.open(self.img_go)
        self.img_go = self.img_go.resize(size=(20, 20,))
        self.img_go = PIL.ImageTk.PhotoImage(image=self.img_go)
        #
        self.btn_go = ttk.Button(
            self.frm_addressbar,
            image=self.img_go,
            command=self._LoadWebsite_starting
        )
        self.btn_go.pack(
            side='right'
        )

        #
        self.lbl_url = ttk.Label(
            master=self.frm_addressbar,
            text='URL:')
        self.lbl_url.pack(
            side='left'
        )

        #
        self.entry_url = ttk.Entry(self.frm_addressbar)
        self.entry_url.pack(
            side='left',
            fill='x',
            expand=1
        )

        #
        self.frm_tags = ttk.Frame(self)
        self.frm_tags.pack(
            fill='both',
            side='top',
            expand=1,
            padx=4,
            pady=(2, 4,)
        )

        # Creating a toolbar...
        self.frm_toolbar = ttk.Frame(self.frm_tags)
        self.frm_toolbar.pack(
            side='top',
            fill='x',
            expand=0     # To achieve fixed height
        )

        # Creating 'Wrap to: ' label...
        self.lbl_wrap = ttk.Label(
            self.frm_toolbar,
            text='Wrap to:'
        )
        self.lbl_wrap.pack(
            side='left',
            padx=(0, 2,)
        )

        # Creating wrap modes combobox...
        self.strvar_wrapModes = tk.StringVar(self)
        self.cmbbx_wrapModes = ttk.Combobox(
            self.frm_toolbar,
            state='readonly',
            width=7,
            textvariable=self.strvar_wrapModes
        )
        self.cmbbx_wrapModes.pack(
            side='left',
            padx=2
        )

        # Creating tagsChecker button...
        # Loading 'open.png'...
        self.img_checkTags = Path(__file__).resolve().parent
        self.img_checkTags = self.img_checkTags / 'res/open.png'
        self.img_checkTags = PIL.Image.open(self.img_checkTags)
        self.img_checkTags = PIL.ImageTk.PhotoImage(image=self.img_checkTags)
        # Creating the button...
        self.btn_tagsChecker = ttk.Button(
            self.frm_toolbar,
            image=self.img_checkTags,
            command=self._CheckTags
        )
        self.btn_tagsChecker.pack(
            side='left',
            padx=2
        )

        # Creating tags scrolled textbox with a horizontal scroll bar...
        self.hscrllbr_tags = ttk.Scrollbar(
            self.frm_tags,
            orient='horizontal'
        )
        self.scrldtxt_tags = ScrolledText(
            self.frm_tags,
            wrap='none'
        )
        self.hscrllbr_tags.config(
            command=self.scrldtxt_tags.xview
        )
        self.scrldtxt_tags.config(
            xscrollcommand=self.hscrllbr_tags.set
        )
        self.hscrllbr_tags.pack(
            side='bottom',
            fill='x'
        )
        self.scrldtxt_tags.pack(
            fill='both',
            side='top',
            expand=1
        )

        # Calling initializer method(s)...
        self._initializeOptions()

        # Binding events...
        self.wait_visibility()
        self.strvar_wrapModes.trace('w', self._onWrapModeChanged)
        self.entry_url.bind('<KeyRelease>', self._OnKeyRelease_url)
        self.scrldtxt_tags.bind('<<Modified>>', self._onTextChanged)

    def _initializeOptions(self):
        self.cmbbx_wrapModes['values'] = [
            wrapMode[1]
            for wrapMode in BeautifierWindow.WRAP_MODES]
        self.cmbbx_wrapModes.current(2)
        self.scrldtxt_tags.config(
            wrap=BeautifierWindow.WRAP_MODES[2][0])

    def _onTextChanged(self, _):
        # The text has been changed, setting background color to white to
        # indicate that the HTML tags structure may  be either correct
        # or incorrect...
        self.scrldtxt_tags['background'] = '#FFFFFF'
        # Setting modified flag to false, to be ready
        # to listen for next modification...
        self.scrldtxt_tags.edit_modified(False)

    def _onWrapModeChanged(self, *_):
        self.scrldtxt_tags.config(
            wrap=BeautifierWindow.WRAP_MODES[
                self.cmbbx_wrapModes.current()][0])

    def _OnKeyRelease_url(self, event):
        if event.keysym == 'Return':
            self._LoadWebsite_starting()

    def _LoadWebsite_starting(self):
        url: str = self.entry_url.get()
        urlParts = urlparse(url)
        if not urlParts.scheme:
            urlParts = list(urlParts)
            urlParts[0] = 'https'
            url = urlunparse(urlParts)
            self.entry_url.delete(0, 'end')
            self.entry_url.insert(0, url)
        asyncHtmlResp = AsyncRequest(
            group=None,
            url=url
        )
        self.entry_url['state'] = tk.DISABLED
        self.btn_go['state'] = tk.DISABLED
        asyncHtmlResp.start()
        self.after(100, self._LoadWebsite_checking, asyncHtmlResp)

    def _LoadWebsite_checking(self, thread: AsyncRequest):
        if thread.is_alive():
            self.after(100, self._LoadWebsite_checking, thread)
        else:
            self.scrldtxt_tags.delete('1.0', 'end')
            self.scrldtxt_tags.insert('1.0', thread.htmlResponse)
            self.entry_url['state'] = tk.NORMAL
            self.btn_go['state'] = tk.NORMAL

    def _CheckTags(self) -> None:
        import warnings
        from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

        # Variables...
        result: bool
        html: str

        # Registering XMLParsedAsHTMLWarning as exception...
        warnings.filterwarnings(action='error',category=XMLParsedAsHTMLWarning)
        # Getting the HTML...
        html = self.scrldtxt_tags.get('1.0', 'end')
        # Checking tags consistency...
        htmlChecker = HtmlTagsChecker()
        result = htmlChecker.feed(html)
        if result:
            # Tags are Ok, chaning the background to green...
            self.scrldtxt_tags['background'] = '#98FFD3'
        else:
            # Tags are NOT Ok, chaning the background to pink...
            self.scrldtxt_tags['background'] = '#FFC6DF'
        # Beatifying the HTML...
        bDialog = BeautifyingDialog(html, indent=3)
        bDialog.mainloop()


def Prettify(text: str) -> str:
    indent = 2
    lines = text.splitlines(keepends=False)
    idx = 0
    while idx < len(lines):
        lspaces = len(lines[idx]) - len(lines[idx].lstrip())
        lines[idx] = (' ' * ((indent - 1) * lspaces)) + lines[idx]
        idx += 1
    return '\n'.join(lines)


if __name__ == '__main__':
    programWindow = BeautifierWindow()
    programWindow.mainloop()
