from node import NodeRoles


def trackers(nodes):
	return filter(lambda n: n.role == NodeRoles.Tracker, nodes)


def peers(nodes):
	return filter(lambda n: n.role == NodeRoles.Peer, nodes)
