from __future__ import division
import random
from copy import copy
from PyQt4 import QtGui, QtCore

import config
from simulation_widget import SimulationWidget
from node import Node, NodeRoles
from torrent_file import TorrentFile
from connection import Connection
from chunk import Chunk
from utils import peers, trackers


class MainWindow(SimulationWidget):

	def __init__(self):
		SimulationWidget.__init__(self)

		random.seed(config.RANDOM_SEED)

		self.nodes = []
		self.files = []
		self.connections = []
		self.chunks = []

		self.steps = 0
		self.total_data = 0
		self.total_files = 0
		self.avg_speed = 0
		self.ratio = 0.0

		self.nodes_layout = QtGui.QVBoxLayout()
		self.NodeListContent.setLayout(self.nodes_layout)
		self.files_layout = QtGui.QVBoxLayout()
		self.FileListContent.setLayout(self.files_layout)
		self.connections_layout = QtGui.QVBoxLayout()
		self.ConnectionListContent.setLayout(self.connections_layout)
		self.chunks_layout = QtGui.QVBoxLayout()
		self.ChunkListContent.setLayout(self.chunks_layout)

		self.connect(self.InitializeButton, QtCore.SIGNAL("clicked()"), self.initialize)
		self.connect(self.StepButton, QtCore.SIGNAL("clicked()"), self.doSteps)
		self.connect(self.CloseAllButton, QtCore.SIGNAL("clicked()"), self.closeAll)
		self.connect(self.InvalidateAllButton, QtCore.SIGNAL("clicked()"), self.invalidateAll)
		self.connect(self.ValidateAllButton, QtCore.SIGNAL("clicked()"), self.validateAll)

		self.update()

	def initialize(self):
		self.clear()

		# generate nodes
		for i in range(0, config.TRACKERS + config.PEERS):
			if i >= config.TRACKERS:
				self.addNode(i, NodeRoles.Peer)
			else:
				self.addNode(i, NodeRoles.Tracker)

		# generate files
		for i in range(0, config.FILES):
			self.addFile("torrent%d" % i, random.randint(*config.FILE_SIZE_RANGE), random.choice(trackers(self.nodes)))

		# distribute files among peers
		files = copy(self.files)
		while len(files) > 0:
			peer = random.choice(peers(self.nodes))
			file = random.choice(files)
			files.remove(file)
			peer.seedFile(file)

		self.announce()

		# give peers files to download
		files = copy(self.files)
		while len(files) > 0:
			peer = random.choice(peers(self.nodes))
			file = random.choice(files)
			if file in [f.file for f in peer.files]:
				continue
			files.remove(file)
			peer.downloadFile(file)

		self.update()

	def addNode(self, nid, role):
		node = Node(nid, role)
		self.nodes.append(node)
		self.nodes_layout.addWidget(node)

	def deleteNode(self, node):
		self.nodes_layout.removeWidget(node)
		self.nodes.remove(node)
		node.deleteLater()

	def addFile(self, name, chunks, tracker):
		file = TorrentFile(name, chunks, tracker)
		self.files.append(file)
		self.files_layout.addWidget(file)

	def deleteFile(self, file):
		self.files_layout.removeWidget(file)
		self.files.remove(file)
		file.deleteLater()

	def addConnection(self, seeder, peer):
		con = Connection(seeder, peer, random.randint(*config.SPEED_RANGE), parent=self)
		self.connections.append(con)
		self.connections_layout.addWidget(con)

	def deleteConnection(self, con):
		self.connections_layout.removeWidget(con)
		self.connections.remove(con)
		con.deleteLater()

	def purgeConnection(self, con):
		for chunk in [c for c in self.chunks if c.con == con]:
			self.deleteChunk(chunk)
		self.deleteConnection(con)
		# self.update(-1)

	def addChunk(self, con, file, n):
		chunk = Chunk(con, file, n)
		self.chunks.append(chunk)
		self.chunks_layout.addWidget(chunk)

	def deleteChunk(self, chunk):
		self.chunks_layout.removeWidget(chunk)
		self.chunks.remove(chunk)
		chunk.deleteLater()

	def clear(self):
		for n in self.nodes:
			self.deleteNode(n)
		for f in self.files:
			self.deleteFile(f)
		for c in self.connections:
			self.deleteConnection(c)
		for c in self.chunks:
			self.deleteChunk(c)

	def announce(self):
		for peer in peers(self.nodes):
			peer.announce(self.nodes)

	def update(self):
		for n in self.nodes:
			n.update(self.steps)
		for f in self.files:
			f.update(self.steps)
		for c in self.connections:
			c.update(self.steps)
		for c in self.chunks:
			c.update(self.steps)

		self.StepsLabel.setText(str(self.steps))
		self.updateStats()

	def updateStats(self):
		self.aggregateSpeed()
		self.updateRatio()

		self.TotalDataLabel.setText("%d K" % self.total_data)
		self.TotalFilesLabel.setText(str(self.total_files))
		self.AvgSpeedLabel.setText("%.2f KB/s" % self.avg_speed)
		self.RatioLabel.setText("%.2f" % self.ratio)

	def aggregateSpeed(self):
		s = sum([c.speed for c in self.connections]) + self.avg_speed
		self.avg_speed = s / (len(self.connections) + 1)

	def updateRatio(self):
		seeds = sum([f.seeds for f in self.files])
		peers = sum([f.peers for f in self.files])
		if peers == 0:
			self.ratio = seeds
		else:
			self.ratio = seeds / peers

	def transmission(self, con):
		con.transmission()
		self.total_data += con.speed

	def doSteps(self):
		for i in range(0, self.StepSpinBox.value()):
			self.step()

	def step(self):
		for peer in peers(self.nodes):
			for file in peer.files:
				if file.progress < 1:
					if not file.peers:
						con = filter(lambda c: c.seeder == file.file.tracker and c.receiver == peer, self.connections)
						if not con:
							# create connection to tracker
							self.addConnection(file.file.tracker, peer)
						else:
							con = con[0]
							chunk = filter(lambda c: c.con == con and c.n == -1, self.chunks)
							if not chunk:
								# get peers from tracker
								self.addChunk(con, None, -1)
							else:
								# transmit peer list
								chunk = chunk[0]
								chunk.setProgress(chunk.progress + con.speed / config.CHUNK_SIZE)
								self.transmission(con)
								if chunk.progress >= 1:
									# finish chunk
									if chunk.valid:
										file.peers = file.file.tracker.getPeers(file.file)
										self.deleteConnection(con)
									self.deleteChunk(chunk)
					else:
						for remote_peer in file.peers:
							con = filter(lambda c: c.seeder == remote_peer and c.receiver == peer, self.connections)
						if not con:
							# create connection to peer
							self.addConnection(remote_peer, peer)
						else:
							con = con[0]
							chunk = filter(lambda c: c.con == con, self.chunks)
							if not chunk:
								# request chunk from peer
								self.addChunk(con, file.file, file.nextChunk())
							else:
								# transmit file data
								chunk = chunk[0]
								chunk.setProgress(chunk.progress + con.speed / config.CHUNK_SIZE)
								self.transmission(con)
								if chunk.progress >= 1:
									# finish chunk
									if chunk.valid:
										file.completeChunk()
										file.setProgress(file.progress + 1 / file.file.chunks)
									# else:
									# 	file.chunk -= 1
									self.deleteChunk(chunk)
									if file.progress >= 1:
										# finish file
										self.total_files += 1
										file.file.finish()
										self.deleteConnection(con)
		self.steps += 1
		self.update()

	def closeAll(self):
		map(self.purgeConnection, self.connections[::-1])

	def invalidateAll(self):
		for c in self.chunks:
			c.valid = False
			c.update(-1)

	def validateAll(self):
		for c in self.chunks:
			c.valid = True
			c.update(-1)
