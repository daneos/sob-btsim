import config
from simulation_widget import SimulationWidget


class Chunk(SimulationWidget):

	def __init__(self, con, file, n, parent=None):
		SimulationWidget.__init__(self, parent)
		self.con = con
		self.file = file
		self.n = n
		self.progress = 0
		self.valid = True

	def update(self, step):
		SimulationWidget.update(self, step)

		if not self.file:
			# -- meta -- chunk
			self.NumberLabel.setText("1")
			self.TotalLabel.setText("1")
			self.SizeLabel.setText(str(config.CHUNK_SIZE))
			self.FilenameLabel.setText("-- meta --")
		else:
			# data chunk
			self.NumberLabel.setText(str(self.n))
			self.TotalLabel.setText(str(self.file.chunks))
			self.SizeLabel.setText(str(self.file.chunks * config.CHUNK_SIZE))
			self.FilenameLabel.setText(self.file.name)
		self.SIDLabel.setText(str(self.con.seeder.id))
		self.CIDLabel.setText(str(self.con.receiver.id))
		self.ProgressBar.setValue(self.progress * 100)

	def setProgress(self, progress):
		self.progress = progress

	def invalidate(self):
		self.valid = False
