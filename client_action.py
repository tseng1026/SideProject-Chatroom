# coding='utf-8'

import socket
import logging
from getpass import getpass

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
		self.action = input("Register (R), Login (L): ")
		self.socket.send(self.action.encode())
		return
	
	def sign_exec(self):
		# input username and password
		username = input  ("Username: ")
		password = getpass("Password: ")
		if self.action == "R": verified = getpass("Verified: ")

		# send to the server
		if self.action == "R" and password != verified: return
		info = username + "\n" + password
		self.socket.send(info.encode())

		# recv from the server
		result = self.socket.recv(1024).decode()

		# update logs
		if result == "F": logging.info("[Action {}] {} login fail.".format(self.action, username))
		if result == "P": logging.info("[Action {}] {} login pass.".format(self.action, username))
		if result == "P": self.action, self.status, self.username = "", 2, username
		return


	### main function
	def main_menu(self):
		self.action = input("Message (M), Add Friend (A), Delete Friend (D), Blocklist (B): ")
		if self.action == "A" or self.action == "D": self.status = 3
		if self.action == "M": self.status = 4
		self.socket.send(self.action.encode())
		return

	def main_friend(self):
		# input peername
		peername = input("Peername: ")

		# send to the server
		data = self.username + "\n" + peername
		self.socket.send(data.encode())

		# recv from the server
		result = self.socket.recv(1024).decode()

		# update logs
		if result == "F": logging.info("[Action {}] {} friend fail.".format(self.action, self.username))
		if result == "P": logging.info("[Action {}] {} friend pass.".format(self.action, self.username))
		if result == "P": self.action, self.status = "", 2
		return

	def main_reading(self):
		while True:
			# recv from the server
			data = self.socket.recv(1024).decode()
			if not data: continue
			sendname, content = data.split("\n", 1)

			# update logs
			logging.info("[Action {}] {} message recv.".format(self.action, self.username))
		return

	def main_writing(self):
		while True:
			# input recvname and content
			recvname, content = input(), input()

			# send to the server
			data = self.username + "\n" + recvname + "\n" + content
			self.socket.send(data.encode())

			# update logs
			logging.info("[Action {}] {} message sent.".format(self.action, self.username))
		return
