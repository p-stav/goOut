users = []
ripples = []

class Ripple:
	def __init__(self, user, text):
		self.receivers = [user]
		self.text = text
		ripples.append(self)

	def __repr__(self):
		return "Ripple text:%s. Number of receivers:%d" % (self.text, len(self.receivers))

	def __str__(self):
		return "Ripple text:%s. Number of receivers:%d" % (self.text, len(self.receivers))

	def addReceivers(self, newReceivers):
		for receiver in newReceivers:
			self.receivers.append(receiver)


class User:
	def __init__(self, name):
		self.pendingRipples = []
		self.name = name
		users.append(self)

	def __repr__(self):
		return "<User name:%s. Number of pending ripples:%d>" % (self.name, len(self.pendingRipples))

	def __str__(self):
		return "User name:%s. Number of pending ripples:%d" % (self.name, len(self.pendingRipples))

	def startRipple(self, text):
		ripple = Ripple(self, text)
		# TODO: function that gets next set of users
		newReceivers = []
		for user in users:
			if user != self:
				newReceivers.append(user)
				user.pendingRipples.append(ripple)
				break

		if newReceivers:
			ripple.addReceivers(newReceivers)

	def spreadRipple(self, ripple):
		# TODO: function that gets next set of users
		newReceivers = []
		for user in users:
			if user not in ripple.receivers:
				newReceivers.append(user)
				user.pendingRipples.append(ripple)
				break

		if newReceivers:
			ripple.addReceivers(newReceivers)
		
		self.pendingRipples.remove(ripple)

	def dismissRipple(self, ripple):
		self.pendingRipples.remove(ripple)




