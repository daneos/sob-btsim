import config
from simulation_widget import SimulationWidget


class TorrentFile(SimulationWidget):
	def __init__(self, name, chunks, tracker, parent=None):
		SimulationWidget.__init__(self, parent)

		self.name = name
		self.chunks = chunks
		self.size = chunks * config.CHUNK_SIZE
		self.tracker = tracker
		self.seeds = 0
		self.peers = 0

	def update(self, step):
		SimulationWidget.update(self, step)

		self.FilenameLabel.setText(self.name)
		self.SizeLabel.setText("%d K" % self.size)
		self.ChunksLabel.setText("%d chunks" % self.chunks)
		self.TrackerLabel.setText(str(self.tracker.id))
		self.SeedsPeersLabel.setText("%d / %d" % (self.seeds, self.peers))

	def seed(self):
		self.seeds += 1

	def download(self):
		self.peers += 1

	def finish(self):
		self.peers -= 1
		self.seeds += 1
