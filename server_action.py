# coding='utf-8'

import socket
import logging
import database

class Action():
	def __init__(self, socket):
		self.socket = socket
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
		return

	def sign_exec(self):
		addr = self.socket.getpeername()

		# recv from the client (content)
		info = self.socket.recv(1024).decode()
		if not info: return
		username, password = info.split("\n", 1)

		# send to the client (shake)
		result = "F"
		if self.action == "L" and database.Account.verify(username, password, addr): result = "P"
		if self.action == "R" and database.Account.insert(username, password, addr): result = "P"
		self.socket.send(result.encode())

		# update logs
		if result == "P": self.action, self.status, self.username = "", 2, username
		if result == "P": logging.info("{}: Successfully sign with username {}.".format(addr, username))
		if result == "F": logging.info("{}: Fail to sign with username {}".format(addr, username))
		return

	### main function
	def main_menu(self):
		self.action = self.socket.recv(1024).decode()
		if self.action == "A" or self.action == "D": self.status = 3
		if self.action == "M": self.status = 4
		return

	def main_friend(self):
		# recv from the client (content)
		data = self.socket.recv(1024).decode()
		if not data: return
		username, peername = data.split("\n", 1)

		# send to the client (shake)
		result = "F"
		if self.action == "A" and database.Friends.insert(username, peername): result = "P"
		if self.action == "D" and database.Friends.delete(username, peername): result = "P"
		self.socket.send(result.encode())
		
		# update logs
		if result == "F": logging.info("{} friend fail.".format(username))
		if result == "P": logging.info("{} friend pass.".format(username))
		if result == "P": self.action, self.status = "", 2
		return

	def main_reading(self):
		# recv from the client
		data = self.socket.recv(1024).decode()
		if not data: return
		self.username, self.peername, content = data.split("\n", 2)
		database.Message.insert(self.username, self.peername, content)

		# update logs
		logging.info("{} -> {} message accept.".format(self.username, self.peername))
		return

	def main_writing(self):
		# send to the client
		content = database.Message.delete(self.username, self.peername)
		if not content: return
		print (content)
		
		data = self.peername + "\n" + content
		self.socket.send(data.encode())


		# update logs
		logging.info("{} -> {} message transfer.".format(self.username, self.peername))
		return
