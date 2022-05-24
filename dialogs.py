import tkinter as tk
from tkinter import ttk


class OutlineDialog(tk.Toplevel):
    def __init__(
            self,
            text: str,
            master: tk.Misc | None = None,
            **kwargs
            ) -> None:

        super().__init__(master, **kwargs)
        self.title('The outline of HTML elements')

        #
        self.frm_container = ttk.Frame(master=self)
        self.frm_container.pack(
            fill='both',
            expand=1)

        #
        self.vscrllbr_outline = ttk.Scrollbar(
            master=self.frm_container,
            orient='vertical')
        self.hscrllbr_outline = ttk.Scrollbar(
            master=self.frm_container,
            orient='horizontal')
        self.txt_outline = tk.Text(
            master=self.frm_container,
            wrap='none',
            xscrollcommand=self.hscrllbr_outline.set,
            yscrollcommand=self.vscrllbr_outline.set)
        self.hscrllbr_outline.config(
            command=self.txt_outline.xview)
        self.vscrllbr_outline.config(
            command=self.txt_outline.yview)
        self.hscrllbr_outline.pack(
            side='bottom',
            fill='x')
        self.vscrllbr_outline.pack(
            side='right',
            fill='y')
        self.txt_outline.pack(
            fill='both',
            expand=1)

        self.txt_outline.insert(
            index='1.0',
            chars=text)
