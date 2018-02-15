#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

version = ''
with open('pyformsd/__init__.py', 'r') as fd: version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
																 fd.read(), re.MULTILINE).group(1)

if not version: raise RuntimeError('Cannot find version information')

setup(
	name='PyFormsD',
	version=version,
	description="""Pyforms is a Python 2.7 and 3.4 framework to develop GUI application,
		which promotes modular software design and code reusability with minimal effort.""",
	author='Ricardo Ribeiro',
	author_email='ricardojvr@gmail.com',
	license='MIT',
	url='https://github.com/dominic-dev/pyformsd',
	install_requires=[
		"anyqt",
	],
	packages=[
		'pyformsd',
		'pyformsd.utils',
		'pyformsd.terminal',
		'pyformsd.terminal.Controls',
		'pyformsd.gui',
		'pyformsd.gui.dialogs',
		'pyformsd.gui.Controls',
		'pyformsd.gui.Controls.ControlEventTimeline',
		'pyformsd.gui.Controls.ControlEventsGraph',
		'pyformsd.gui.Controls.ControlPlayer'],

	package_data={'pyformsd': [
		'gui/Controls/uipics/*.png',
		'gui/mainWindow.ui', 'gui/Controls/*.ui', 'gui/Controls/ControlPlayer/*.ui',
		'gui/Controls/ControlEventTimeline/*.ui']
	},
)
