#!/usr/bin/env python2.7

import sys
from signal import signal, SIGINT, SIG_DFL
from PyQt4 import QtGui

from main_window import MainWindow


def main():
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	signal(SIGINT, SIG_DFL)			# exit on Ctrl+C
	main()
