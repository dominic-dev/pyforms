#!/usr/bin/python
# -*- coding: utf-8 -*-

from pysettings import conf

from pyforms.gui.Controls.ControlFile import ControlFile

import pyforms.utils.tools as tools


from AnyQt 			 import uic
from AnyQt.QtWidgets import QFileDialog


class ControlSaveFile(ControlFile):

	def click(self):
		value = QFileDialog.getSaveFileName(self.parent, self._label, self.value, self.filter)
		
		if conf.PYFORMS_USE_QT5:
			value = value[0]
		else:
			value = str(value)

		if value and len(value)>0: self.value = value

