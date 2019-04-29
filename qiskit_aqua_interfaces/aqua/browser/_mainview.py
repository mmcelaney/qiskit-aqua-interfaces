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

import sys
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.ttk as ttk
from tkinter import font
import webbrowser
from ._controller import Controller
from ._sectionsview import SectionsView
from ._sectionpropertiesview import SectionPropertiesView
from ._emptyview import EmptyView
from qiskit_aqua_interfaces import __version__
from qiskit_aqua_interfaces.aqua.user_interface import UIPreferences


class MainView(ttk.Frame):

    _HELP_LINK = 'http://qiskit.org/documentation/aqua/'

    def __init__(self, parent=None):
        """Create MainView object."""
        super(MainView, self).__init__(parent)
        self._controller = Controller(self)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self._create_widgets()
        self.master.title('Qiskit Aqua Browser')
        if parent is not None:
            parent.protocol('WM_DELETE_WINDOW', self.quit)

    def _show_about_dialog(self):
        tkmb.showinfo(message='Qiskit Aqua Browser {}'.format(__version__))

    def _create_widgets(self):
        self._makeMenuBar()
        self._create_pane()

    def _makeMenuBar(self):
        menubar = tk.Menu(self.master)
        if sys.platform == 'darwin':
            app_menu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=app_menu)
            app_menu.add_command(label='About Qiskit Aqua Browser', command=self._show_about_dialog)
            self.master.createcommand('tk::mac::Quit', self.quit)

        self.master.config(menu=menubar)
        self._controller._filemenu = self._fileMenu(menubar)

        help_menu = tk.Menu(menubar, tearoff=False)
        if sys.platform != 'darwin':
            help_menu.add_command(label='About Qiskit Aqua Browser', command=self._show_about_dialog)

        help_menu.add_command(label='Open Help Center', command=self._open_help_center)
        menubar.add_cascade(label='Help', menu=help_menu)

    def _open_help_center(self):
        webbrowser.open(MainView._HELP_LINK)

    def _fileMenu(self, menubar):
        if sys.platform != 'darwin':
            file_menu = tk.Menu(menubar, tearoff=False)
            file_menu.add_separator()
            file_menu.add_command(label='Exit', command=self.quit)
            menubar.add_cascade(label='File', menu=file_menu)
            return file_menu

        return None

    def _create_pane(self):
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(expand=tk.YES, fill=tk.BOTH)
        top_pane = ttk.PanedWindow(main_pane, orient=tk.HORIZONTAL)
        top_pane.pack(expand=tk.YES, fill=tk.BOTH)
        main_pane.add(top_pane)

        self._controller._sectionsView = SectionsView(self._controller, top_pane)
        self._controller._sectionsView.pack(expand=tk.YES, fill=tk.BOTH)
        top_pane.add(self._controller._sectionsView)

        main_container = tk.Frame(top_pane)
        main_container.pack(expand=tk.YES, fill=tk.BOTH)
        style = ttk.Style()
        style.configure('PropViewTitle.TLabel',
                        borderwidth=1,
                        relief=tk.RIDGE,
                        anchor=tk.CENTER)
        label = ttk.Label(main_container,
                          style='PropViewTitle.TLabel',
                          padding=(5, 5, 5, 5),
                          textvariable=self._controller._sectionsView_title)
        label_font = font.nametofont('TkHeadingFont').copy()
        label_font.configure(size=12, weight='bold')
        label['font'] = label_font

        label.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        container = tk.Frame(main_container)
        container.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self._controller._emptyView = EmptyView(container)
        self._controller._emptyView.grid(row=0, column=0, sticky='nsew')

        self._controller._propertiesView = SectionPropertiesView(self._controller, container)
        self._controller._propertiesView.grid(row=0, column=0, sticky='nsew')
        self._controller._emptyView.tkraise()
        top_pane.add(main_container, weight=1)

        self.update_idletasks()
        self.after(0, self._controller.populate_sections)

    def quit(self):
        if tkmb.askyesno('Verify quit', 'Are you sure you want to quit?'):
            preferences = UIPreferences()
            preferences.set_browser_geometry(self.master.winfo_geometry())
            preferences.save()
            ttk.Frame.quit(self)
            return True

        return False
