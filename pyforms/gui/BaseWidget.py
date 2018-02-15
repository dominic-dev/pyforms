#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import json
import subprocess
import time, sys
from datetime import datetime, timedelta

from pysettings import conf

if conf.PYFORMS_USE_QT5:
	from PyQt5.QtWidgets import QFrame
	from PyQt5.QtWidgets import QVBoxLayout
	from PyQt5.QtWidgets import QTabWidget
	from PyQt5.QtWidgets import QSplitter
	from PyQt5.QtWidgets import QHBoxLayout
	from PyQt5.QtWidgets import QSpacerItem
	from PyQt5.QtWidgets import QSizePolicy
	from PyQt5.QtWidgets import QLabel
	from PyQt5.QtGui import QFont
	from PyQt5.QtWidgets import QFileDialog
	from PyQt5.QtWidgets import QApplication
	from PyQt5 import QtCore

else:
	from PyQt4.QtGui import QFrame
	from PyQt4.QtGui import QVBoxLayout
	from PyQt4.QtGui import QTabWidget
	from PyQt4.QtGui import QSplitter
	from PyQt4.QtGui import QHBoxLayout
	from PyQt4.QtGui import QSpacerItem
	from PyQt4.QtGui import QSizePolicy
	from PyQt4.QtGui import QLabel
	from PyQt4.QtGui import QFont
	from PyQt4.QtGui import QFileDialog
	from PyQt4.QtGui import QApplication
	from PyQt4 import QtCore

from pyforms.gui.Controls.ControlBase import ControlBase
from pyforms.gui.Controls.ControlProgress import ControlProgress


class BaseWidget(QFrame):
	"""
	The class implements the most basic widget or window.
	"""

	def __init__(self, title='Untitled', parent_win=None, win_flag=None):
		if parent_win is not None and win_flag is None: win_flag = QtCore.Qt.Dialog

		QFrame.__init__(self) if parent_win is None else QFrame.__init__(self, parent_win, win_flag)

		# self.setObjectName(self.__class__.__name__)


		layout = QVBoxLayout()
		self.setLayout(layout)
		
		if conf.PYFORMS_USE_QT5:
			layout.setContentsMargins(0,0,0,0)
		else:
			layout.setMargin(0)

		self.title = title
		self.has_progress = False

		self._mainmenu = []
		self._splitters = []
		self._tabs = []
		self._formset = None
		self._formLoaded = False
		self.uid = id(self)

		self.setAccessibleName('BaseWidget')

	##########################################################################
	############ FUNCTIONS  ##################################################
	##########################################################################


	def init_form(self):
		"""
		Generate the module Form
		"""
		if not self._formLoaded:

			if self.has_progress:
				self._progress = ControlProgress("Progress", 0, 100)
				self._progress.hide()
				if self._formset != None:
					self._formset += ['_progress']

			if self._formset is not None:
				control = self.generate_panel(self._formset)
				self.layout().addWidget(control)
			else:
				allparams = self.controls
				for key, param in allparams.items():
					param.parent = self
					param.name = key
					self.layout().addWidget(param.form)
			self._formLoaded = True

	def set_margin(self, margin):
		if conf.PYFORMS_USE_QT5:
			self.layout().setContentsMargins(margin,margin,margin,margin)
		else:
			self.layout().setMargin(margin)


	def generate_tabs(self, formsetdict):
		"""
		Generate QTabWidget for the module form
		@param formset: Tab form configuration
		@type formset: dict
		"""
		tabs = QTabWidget(self)
		for key, item in sorted(formsetdict.items()):
			ctrl = self.generate_panel(item)
			tabs.addTab(ctrl, key[key.find(':') + 1:])
		return tabs

	def generate_panel(self, formset):
		"""
		Generate a panel for the module form with all the controls
		formset format example: [('_video', '_arenas', '_run'), {"Player":['_threshold', "_player", "=", "_results", "_query"], "Background image":[(' ', '_selectBackground', '_paintBackground'), '_image']}, "_progress"]
		tuple: will display the controls in the same horizontal line
		list: will display the controls in the same vertical line
		dict: will display the controls in a tab widget
		'||': will plit the controls in a horizontal line
		'=': will plit the controls in a vertical line
		@param formset: Form configuration
		@type formset: list
		"""
		control = None
		if '=' in formset:
			control = QSplitter(QtCore.Qt.Vertical)
			tmp = list(formset)
			index = tmp.index('=')
			firstPanel = self.generate_panel(formset[0:index])
			secondPanel = self.generate_panel(formset[index + 1:])
			control.addWidget(firstPanel)
			control.addWidget(secondPanel)
			self._splitters.append(control)
			return control
		elif '||' in formset:
			control = QSplitter(QtCore.Qt.Horizontal)
			tmp = list(formset)
			rindex = lindex = index = tmp.index('||')
			rindex -= 1
			rindex += 2
			if isinstance(formset[lindex - 1], int):
				lindex = lindex - 1
			if len(formset) > rindex and isinstance(formset[index + 1], int):
				rindex += 1
			firstPanel = self.generate_panel(formset[0:lindex])
			secondPanel = self.generate_panel(formset[rindex:])
			if isinstance(formset[index - 1], int):
				firstPanel.setMaximumWidth(formset[index - 1])
			if isinstance(formset[index + 1], int):
				secondPanel.setMaximumWidth(formset[index + 1])
			control.addWidget(firstPanel)
			control.addWidget(secondPanel)
			self._splitters.append(control)
			return control
		control = QFrame(self)
		layout = None
		if type(formset) is tuple:
			layout = QHBoxLayout()
			for row in formset:
				if isinstance(row, (list, tuple)):
					panel = self.generate_panel(row)
					layout.addWidget(panel)
				elif row == " ":
					spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
					layout.addItem(spacer)
				elif type(row) is dict:
					c = self.generate_tabs(row)
					layout.addWidget(c)
					self._tabs.append(c)
				else:
					param = self.controls.get(row, None)
					if param is None:
						label = QLabel()
						label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
						# layout.addWidget( label )

						if row.startswith('info:'):
							label.setText(row[5:])
							font = QFont()
							font.setPointSize(10)
							label.setFont(font)
							label.setAccessibleName('info')
						elif row.startswith('h1:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(17)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h1')
						elif row.startswith('h2:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(16)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h2')
						elif row.startswith('h3:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(15)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h3')
						elif row.startswith('h4:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(14)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h4')
						elif row.startswith('h5:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(12)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h5')
						else:
							label.setText(row)
							font = QFont()
							font.setPointSize(10)
							label.setFont(font)
							label.setAccessibleName('msg')
						label.setToolTip(label.text())
						layout.addWidget(label)
					else:
						param.parent = self
						param.name = row
						layout.addWidget(param.form)
		elif type(formset) is list:
			layout = QVBoxLayout()
			for row in formset:
				if isinstance(row, (list, tuple)):
					panel = self.generate_panel(row)
					layout.addWidget(panel)
				elif row == " ":
					spacer = QSpacerItem(
						20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
					layout.addItem(spacer)
				elif type(row) is dict:
					c = self.generate_tabs(row)
					layout.addWidget(c)
					self._tabs.append(c)
				else:
					param = self.controls.get(row, None)
					if param is None:
						label = QLabel()
						label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
						label.resize(30, 30)
						# layout.addWidget( label )

						if row.startswith('info:'):
							label.setText(row[5:])
							font = QFont()
							font.setPointSize(10)
							label.setFont(font)
							label.setAccessibleName('info')
						elif row.startswith('h1:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(17)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h1')
						elif row.startswith('h2:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(16)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h2')
						elif row.startswith('h3:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(15)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h3')
						elif row.startswith('h4:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(14)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h4')
						elif row.startswith('h5:'):
							label.setText(row[3:])
							font = QFont()
							font.setPointSize(12)
							font.setBold(True)
							label.setFont(font)
							label.setAccessibleName('h5')
						else:
							label.setText(row)
							font = QFont()
							font.setPointSize(10)
							label.setFont(font)
							label.setAccessibleName('msg')

						label.setToolTip(label.text())

						layout.addWidget(label)
					else:
						param.parent = self
						param.name = row
						layout.addWidget(param.form)
		
		if conf.PYFORMS_USE_QT5:
			layout.setContentsMargins(0,0,0,0)
		else:
			layout.setMargin(0)
			
		control.setLayout(layout)
		return control

	def show(self):
		"""
		It shows the 
		"""
		self.init_form()
		super(BaseWidget, self).show()

	def save_form(self, data={}, path=None):
		allparams = self.controls

		if hasattr(self, 'load_order'):
			for name in self.load_order:
				param = allparams[name]
				data[name] = {}
				param.save_form(data[name])
		else:
			for name, param in allparams.items():
				data[name] = {}
				param.save_form(data[name])
		return data

	def load_form(self, data, path=None):
		allparams = self.controls

		if hasattr(self, 'load_order'):
			for name in self.load_order:
				param = allparams[name]
				if name in data:
					param.load_form(data[name])
		else:
			for name, param in allparams.items():
				if name in data:
					param.load_form(data[name])
				# self.init_form()

	def save_window(self):
		allparams = self.controls
		data = {}
		self.save_form(data)

		filename = QFileDialog.getSaveFileName(self, 'Select file')
		with open(filename, 'w') as output_file: json.dump(data, output_file)

	def load_form_filename(self, filename):
		with open(filename, 'r') as pkl_file:
			project_data = json.load(pkl_file)
		data = dict(project_data)
		self.load_form(data)

	def load_window(self):
		filename = QFileDialog.getOpenFileNames(self, 'Select file')
		self.load_form_filename(str(filename[0]))

	##########################################################################
	############ EVENTS ######################################################
	##########################################################################

	def before_close_event(self):
		""" 
		Do something before closing widget 
		Note that the window will be closed anyway    
		"""
		pass

	##########################################################################
	############ Properties ##################################################
	##########################################################################

	@property
	def form_has_loaded(self):
		return self._formLoaded

	@property
	def controls(self):
		"""
		Return all the form controls from the the module
		"""
		result = {}
		for name, var in vars(self).items():
			try:
				if isinstance(var, ControlBase):
					result[name] = var
			except:
				pass
		return result

	@property
	def form(self):
		return self

	@property
	def title(self):
		return self.windowTitle()

	@title.setter
	def title(self, value):
		self.setWindowTitle(value)

	@property
	def mainmenu(self):
		return self._mainmenu

	@mainmenu.setter
	def mainmenu(self, value):
		self._mainmenu = value

	@property
	def formset(self):
		return self._formset

	@formset.setter
	def formset(self, value):
		self._formset = value

	@property
	def uid(self):
		return self._uid

	@uid.setter
	def uid(self, value):
		self._uid = value

	@property
	def max_progress(self):
		return self._progress.max

	@max_progress.setter
	def max_progress(self, value):
		self._progress.max = value

	@property
	def min_progress(self):
		return self._progress.min

	@min_progress.setter
	def min_progress(self, value):
		self._progress.min = value

	@property
	def progress(self):
		return self._progress.value

	@progress.setter
	def progress(self, value):
		self._progress.value = value
		QApplication.processEvents()

		if value == self.max_progress: self._progress.hide()
		if value == self.min_progress: self._progress.show()

	@property
	def visible(self):
		return self.isVisible()

	@visible.setter
	def visible(self, value):
		self.show() if value else self.hide()

	##########################################################################
	############ PRIVATE FUNCTIONS ###########################################
	##########################################################################
	def closeEvent(self, event):
		self.before_close_event()
		super(BaseWidget, self).closeEvent(event)
