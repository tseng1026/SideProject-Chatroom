# coding='utf-8'

import socket
import logging
import database

class Action():
	def __init__(self, socket):
		self.socket  = socket
		self.address = socket.getpeername()

		self.action = ""
		self.status = 0
		self.username = ""
		self.peername = ""

	### status info
	def get_status(self): return self.status	
	def set_status(self, status):
		self.status = status
		return

	### action info
	def get_action(self): return self.action
	def set_action(self, action):
		self.action = action
		return

	### signup or signin
	def sign_menu(self):
		self.status = 1
		self.action = self.socket.recv(1024).decode()
		if not self.action: self.status = -1; return
		logging.info("{}: Choose action {}.".format(self.address, self.action))
		return

	def sign_exec(self):
		# recv from the client (content)
		info = self.socket.recv(1024).decode()
		if not info: self.status = -1; return
		username, password = info.split("\n")

		# send to the client (shake)
		result = "F"
		if self.action == "L" and database.Account.verify(username, password, self.address): result = "P"
		if self.action == "R" and database.Account.insert(username, password, self.address): result = "P"
		self.socket.send(result.encode())

		# update logs
		if result == "P": self.action, self.status, self.username = "", 2, username
		logging.info("{}: User \"{}\" logins ({}).".format(self.address, username, result))
		return

	### main function
	def main_menu(self):
		self.action = self.socket.recv(1024).decode()
		if self.action == "F" or self.action == "P": self.status = 3
		if self.action == "A" or self.action == "D": self.status = 4
		if self.action == "M": self.status = 5
		if not self.action: self.status = -1; return
		logging.info("{}: Choose action {}.".format(self.address, self.action))
		return

	def main_friend_exec(self):
		# recv from the client (content)
		data = self.socket.recv(1024).decode()
		if not data: self.status = -1; return
		username, peername = data.split("\n")

		# send to the client (shake)
		result = "F"
		if self.action == "A" and database.Friends.insert(username, peername): result = "P"
		if self.action == "D" and database.Friends.delete(username, peername): result = "P"
		if self.action == "P" and database.Friends.accept(username, peername): result = "P"
		self.socket.send(result.encode())
		
		# update logs
		if result == "P": self.action, self.status = "", 2
		logging.info("{}: User \"{}\" adds / deletes / accepts friend \"{}\" ({}).".format(self.address, username, peername, result))
		return

	def main_friend_list(self):
		# send to the client
		data1 = database.Friends.friend(self.username, 1)
		data2 = database.Friends.friend(self.username, 0)
		if not data1 or not data2: return

		data = ""
		data += " ".join(str(x[0]) for x in data1) + "\n"
		data += " ".join(str(x[0]) for x in data2)
		print (data)
		# data = self.peername + "\n" + content
		self.socket.send(data.encode())

		# update logs
		logging.info("{}: User \"{}\"\'s friend list.".format(self.address, self.username))
		if self.action == "F": self.status = 2
		if self.action == "P": self.status = 4
		return

	def main_reading(self):
		# recv from the client
		data = self.socket.recv(1024).decode()
		if not data: self.status = -1; return
		self.username, self.peername, content = data.split("\n", 2)
		database.Message.insert(self.username, self.peername, content)

		# update logs
		logging.info("{}: User \"{}\" to user \"{}\"\'s message accepted by server.".format(self.address, self.username, self.peername))
		return

	def main_writing(self):
		# send to the client
		content = database.Message.delete(self.peername, self.username)
		if not content: return
		
		data = self.peername + "\n" + content
		self.socket.send(data.encode())

		# update logs
		logging.info("{}: User \"{}\" to user \"{}\"\'s message transfered by server.".format(self.address, self.username, self.peername))
		return

