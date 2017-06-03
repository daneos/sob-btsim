from PyQt4 import QtGui

from simulation_widget import SimulationWidget


class Connection(SimulationWidget):
	def __init__(self, seeder, receiver, speed, parent=None):
		SimulationWidget.__init__(self, parent)
		self.seeder = seeder
		self.receiver = receiver
		self.speed = speed
		self.transmitted = 0
		self.parent = parent

	def update(self, step):
		SimulationWidget.update(self, step)

		self.SIDLabel.setText(str(self.seeder.id))
		self.CIDLabel.setText(str(self.receiver.id))
		self.SpeedLabel.setText("%d KB/s" % self.speed)
		self.TotalLCD.display(self.transmitted)

	def transmission(self):
		self.transmitted += self.speed

	def contextMenuEvent(self, ev):
		menu = QtGui.QMenu(self)
		close = menu.addAction("Close connection")
		action = menu.exec_(self.mapToGlobal(ev.pos()))

		if action == close:
			if self.parent:
				self.parent.purgeConnection(self)
