from PyQt4 import QtGui

from simulation_widget import SimulationWidget


class NodeRoles:
	Tracker = "Tracker"
	Peer = "Peer"


class Node(SimulationWidget):
	def __init__(self, nid, role, parent=None):
		SimulationWidget.__init__(self, parent)

		self.id = nid
		self.role = role

		self.files = []
		self.peers = []
		self.connections = []
		self.list_layout = QtGui.QVBoxLayout()
		self.ListContent.setLayout(self.list_layout)

	def update(self, step):
		SimulationWidget.update(self, step)

		self.IDLabel.setText(str(self.id))
		self.RoleLabel.setText(self.role)
		for f in self.files:
			f.update(step)
		for p in self.peers:
			p.update(step)

	def seedFile(self, file):
		f = FileListWidget(file, 1)
		self.files.append(f)
		self.list_layout.addWidget(f)
		file.seed()

	def announce(self, nodes):
		for file in self.files:
			# tracker = nodes[file.file.tracker.id]
			file.file.tracker.peerAnnounce(self, file)

	def peerAnnounce(self, peer, file):
		p = self.getClient(peer)
		p.addFile(file)

	def getClient(self, peer):
		client = None
		for p in self.peers:
			if p.peer == peer:
				client = p
		if not client:
			client = ClientListWidget(peer)
			self.peers.append(client)
			self.list_layout.addWidget(client)
		return client

	def downloadFile(self, file):
		f = FileListWidget(file, 0)
		self.files.append(f)
		self.list_layout.addWidget(f)
		file.download()

	def getConnections(self):
		return self.connections

	def getPeers(self, file):
		r = []
		for p in self.peers:
			if file in [f.file for f in p.files]:
				r.append(p.peer)
		return r


class FileListWidget(SimulationWidget):
	def __init__(self, file, progress, parent=None):
		SimulationWidget.__init__(self, parent)

		self.file = file
		self.peers = []
		self.chunk = 0
		self.progress = progress

		self.update(0)

	def update(self, step):
		SimulationWidget.update(self, step)

		self.FilenameLabel.setText(self.file.name)
		self.ProgressBar.setValue(self.progress * 100)

		if self.progress >= 1:
			self.ProgressBar.setFormat("seeding")

	def setProgress(self, progress):
		self.progress = progress

	def setPeers(self, peers):
		self.peers = peers

	def nextChunk(self):
		self.chunk += 1
		return self.chunk


class ClientListWidget(SimulationWidget):
	def __init__(self, peer, parent=None):
		SimulationWidget.__init__(self, parent)

		self.peer = peer
		self.files = []

		self.update(0)

	def update(self, step):
		SimulationWidget.update(self, step)

		self.IDLabel.setText(str(self.peer.id))
		self.FilesLabel.setText("%d files" % len(self.files))

	def addFile(self, file):
		self.files.append(file)
