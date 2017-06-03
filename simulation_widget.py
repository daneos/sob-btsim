from PyQt4 import QtGui, uic


class SimulationWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		uic.loadUi("ui/%s.ui" % self.__class__.__name__, self)

	def update(self, step):
		pass
