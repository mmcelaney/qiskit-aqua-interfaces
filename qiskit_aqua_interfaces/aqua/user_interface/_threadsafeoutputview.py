# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM Corp. 2017 and later.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import tkinter as tk
from tkinter.font import Font
from ._scrollbarview import ScrollbarView
from ._customwidgets import TextCustom
import queue
import string
import platform


class ThreadSafeOutputView(ScrollbarView):

    _DELAY = 50
    _TOTAL_ITERATIONS = 120
    _FULL_BLOCK_CHAR = u'█'
    _CR = '\r'
    _LF = '\n'
    _FONT_FAMILIES = {
            'Darwin': 'Menlo Regular',
    }

    def __init__(self, parent, **options):
        super(ThreadSafeOutputView, self).__init__(parent, **options)
        self._queue = queue.Queue()
        self._textWidget = TextCustom(self, wrap=tk.NONE, state=tk.DISABLED)
        font_family = ThreadSafeOutputView._FONT_FAMILIES.get(platform.system())
        if font_family:
            f = Font(family=font_family)
            self._textWidget.configure(font=f)
        self.init_widgets(self._textWidget)
        self._updateText()

    def _updateText(self):
        try:
            iterations = 0
            while iterations < ThreadSafeOutputView._TOTAL_ITERATIONS:
                line = self._queue.get_nowait()
                iterations += 1
                if line is None:
                    self._write()
                else:
                    self._write(str(line), False)

                self.update_idletasks()
        except:
            pass

        self.after(ThreadSafeOutputView._DELAY, self._updateText)

    def write(self, text):
        if text is None:
            return

        text = str(text)
        if len(text) == 0:
            return

        # remove any non printable character that will cause the Text widget to hang
        text = ''.join([x if x == ThreadSafeOutputView._FULL_BLOCK_CHAR or
                        x in string.printable else '' for x in text])
        if platform.system() == 'Windows':  # Under Windows unicode block is escaped
            text = text.replace('\\u2588', u"\u2588")
        if len(text) == 0:
            return

        # break cr into separate queue entries
        pos = text.find(ThreadSafeOutputView._CR)  # look for cr in text
        while pos >= 0:  # text contains cr
            line = text[:pos]  # up to but not including the end cr
            if len(line) > 0:
                self._queue.put(line)

            text = text[pos:]  # get text with cr in front
            pos = text.find(ThreadSafeOutputView._CR, 1)  # look for cr in text after first pos

        if len(text) > 0:  # insert any remaining text
            self._queue.put(text)

    def flush(self):
        pass

    def buffer_empty(self):
        return self._queue.empty()

    def clear_buffer(self):
        """
        Create another queue to ignore current queue output
        """
        self._queue = queue.Queue()

    def write_line(self, text):
        self.write(text + '\n')

    def clear(self):
        self._queue.put(None)

    def _write(self, text=None, erase=True):
        self._textWidget.config(state=tk.NORMAL)
        if erase:
            self._textWidget.delete(1.0, tk.END)

        if text is not None:
            self._write_text(text)
            pos = self._vscrollbar.get()[1]
            # scrolls only when scroll bar is at the bottom
            if pos == 1.0:
                self._textWidget.yview(tk.END)

        self._textWidget.config(state=tk.DISABLED)

    def _write_text(self, text):
        new_text = text
        pos = new_text.find(ThreadSafeOutputView._CR)  # look for cr in new text
        while pos >= 0:  # new text contains cr
            line = new_text[:pos]  # up to but not including the cr
            if len(line) > 0:
                self._textWidget.insert(tk.END, line)

            # look for last lf
            prev_index_lf = self._textWidget.search(ThreadSafeOutputView._LF,
                                                    '{}-1c'.format(tk.END),
                                                    '1.0',
                                                    backwards=True)
            if prev_index_lf:
                # remove previous line after lf
                self._textWidget.delete('{} + 1c'.format(prev_index_lf), '{}-1c'.format(tk.END))
            else:
                # remove whole text
                self._textWidget.delete(1.0, tk.END)

            new_text = new_text[pos+1:]  # get text after cr
            pos = new_text.find(ThreadSafeOutputView._CR)  # look for cr in new text

        if len(new_text) > 0:  # insert any remaining text
            self._textWidget.insert(tk.END, new_text)
