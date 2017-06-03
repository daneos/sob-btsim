from simulation_widget import SimulationWidget


class Connection(SimulationWidget):
	def __init__(self, seeder, receiver, speed, parent=None):
		SimulationWidget.__init__(self, parent)
		self.seeder = seeder
		self.receiver = receiver
		self.speed = speed
		self.transmitted = 0

	def update(self, step):
		SimulationWidget.update(self, step)

		self.SIDLabel.setText(str(self.seeder.id))
		self.CIDLabel.setText(str(self.receiver.id))
		self.SpeedLabel.setText("%d KB/s" % self.speed)
		self.TotalLCD.display(self.transmitted)

	def transmission(self):
		self.transmitted += self.speed
