import tkinter as tk
from tkinter import ttk
import  warnings
#from xml.etree.ElementTree import tostring

from lxml import etree
from lxml.etree import HTMLParser, _ElementTree, _Element


class BeautifyingDialog(tk.Toplevel):
    def __init__(
            self,
            markup: str,
            master: tk.Misc | None = None,
            indent: int = 2,
            **kwargs
            ) -> None:
        super().__init__(master, **kwargs)
        self.title('The outline of HTML elements')

        self._markup = markup
        self._indent = indent

        root = etree.HTML(self._markup, etree.HTMLParser())
        self._dom: _ElementTree = etree.ElementTree(root)

        self._InitGui()
        self._Prettify()
    
    def _InitGui(self) -> None:
        #
        self._frm_container = ttk.Frame(self)
        self._frm_container.columnconfigure(0, weight=1)
        self._frm_container.rowconfigure(0, weight=1)
        self._frm_container.pack(
            fill='both',
            expand=1)

        #
        self._vscrllbr = ttk.Scrollbar(
            self._frm_container,
            orient='vertical')
        self._hscrllbr = ttk.Scrollbar(
            self._frm_container,
            orient='horizontal')
        self._txt = tk.Text(
            self._frm_container,
            wrap='none',
            xscrollcommand=self._hscrllbr.set,
            yscrollcommand=self._vscrllbr.set)
        self._hscrllbr.config(
            command=self._txt.xview)
        self._vscrllbr.config(
            command=self._txt.yview)
        self._hscrllbr.grid(
            column=0,
            row=1,
            sticky=tk.NSEW)
        self._vscrllbr.grid(
            column=1,
            row=0,
            sticky=tk.NSEW)
        self._txt.grid(
            column=0,
            row=0,
            sticky=tk.NSEW)
        
        #
        self._szgrp = ttk.Sizegrip(self._frm_container)
        self._szgrp.grid(
            column=1,
            row=1,
            sticky=tk.NSEW)
    
    def _Prettify_mmm(self) -> None:
        self._txt.delete('1.0', 'end')
        self._txt.insert('1.0', etree.tostring(self._dom, pretty_print=True))
    
    def _Prettify(self) -> None:
        result: list[str] = [self._dom.docinfo.doctype,]
        result += self._Prettify_recur(self._dom.getroot(), 0)
        self._txt.delete('1.0', 'end')
        for idx in range(len(result)):
            self._txt.insert(f'end', result[idx] + '\n')

    def _Prettify_recur(
            self,
            elem: _Element,
            level: int
            ) -> list[str]:
        from megacodist.html import SINGLETON_ELEMS
        children: list[str] = []
        for child in elem:
            children += self._Prettify_recur(child, level + 1)
        leadingSpace = ' ' * (level * self._indent)
        attrs = ' '.join([
            f'{attr}="{value}"'
            for attr, value in elem.attrib.items()])
        startTag = elem.tag
        if attrs:
            startTag += (' ' + attrs)
        text = None
        if elem.text:
            text = elem.text.strip()
        tail = None
        if elem.tail:
            tail = elem.tail.strip()
        # Forming the result...
        if children:
            children.insert(0, leadingSpace + f'<{startTag}>')
            if text:
                children.insert(1, leadingSpace + (' ' * self._indent) + text)
            if tail:
                children.append(leadingSpace + (' ' * self._indent) + text)
            children.append(leadingSpace + f'</{elem.tag}>')
        elif text:
            children.insert(0, leadingSpace + f'<{startTag}>{text}</{elem.tag}>')
        else:
            if elem.tag in SINGLETON_ELEMS:
                children.insert(0, leadingSpace + f'<{startTag} />')
            else:
                children.insert(0, leadingSpace + f'<{startTag}></{elem.tag}>')
        return children


class OutlineDialog(tk.Toplevel):
    def __init__(
            self,
            text: str,
            master: tk.Misc | None = None,
            **kwargs
            ) -> None:

        super().__init__(master, **kwargs)
        self.title('The outline of HTML elements')

        self._dom:_ElementTree = fromstring(text)

        #
        self._frm_container = ttk.Frame(self)
        self._frm_container.columnconfigure(0, weight=1)
        self._frm_container.rowconfigure(0, weight=1)
        self._frm_container.pack(
            fill='both',
            expand=1)

        #
        self._vscrllbr = ttk.Scrollbar(
            self._frm_container,
            orient='vertical')
        self._hscrllbr = ttk.Scrollbar(
            self._frm_container,
            orient='horizontal')
        self._txt = ttk.Treeview(
            self._frm_container,
            xscrollcommand=self._hscrllbr.set,
            yscrollcommand=self._vscrllbr.set)
        self._txt.heading('#0', anchor=tk.W)
        self._txt.column(
            '#0',
            width=200,
            stretch=False,
            anchor=tk.W)
        self._hscrllbr.config(
            command=self._txt.xview)
        self._vscrllbr.config(
            command=self._txt.yview)
        self._hscrllbr.grid(
            column=0,
            row=1,
            sticky=tk.NSEW)
        self._vscrllbr.grid(
            column=1,
            row=0,
            sticky=tk.NSEW)
        self._txt.grid(
            column=0,
            row=0,
            sticky=tk.NSEW)
        
        self._Populate()
    
    def _Populate(self) -> None:
        #
        childIid = self._txt.insert(
            parent='',
            index='end',
            text=self._dom.tag,
            open=True)
        self._Populate_recur(childIid, self._dom)

    def _Populate_recur(
            self,
            iid: str,
            elem: _Element
            ) -> None:
        if elem.text:
            itemText = elem.text.strip()
            if iid and itemText:
                self._txt.insert(
                    parent=iid,
                    index='end',
                    text=itemText)
        for childElem in elem:
            childIid = self._txt.insert(
                parent=iid,
                index='end',
                text=childElem.tag,
                open=True)
            self._Populate_recur(childIid, childElem)
