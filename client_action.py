# coding='utf-8'

import socket
import logging
from hashlib import sha256
from getpass import getpass

class Action():
	def __init__(self, socket):
		self.socket = socket
		self.address = socket.getpeername()
		
		self.action = ""
		self.inputs = ""
		self.result = ""

		self.username = ""
		self.peername = ""

		self.status = 1
		self.note = []

	### action info
	def get_action(self): return self.action
	def set_action(self, action):
		self.action = action
		return

	def notice(self):
		if   self.action == "" : self.note = ["Action: "]
		elif self.action == "R": self.note = ["Username: ", "Password: "]
		elif self.action == "L": self.note = ["Username: ", "Password: "]
		elif self.action == "A": self.note = ["", "Peername: "]
		elif self.action == "D": self.note = ["", "Peername: "]
		elif self.action == "P": self.note = ["", "Peername: "]
		elif self.action == "F": self.note = [""]
		return 

	def get_inputs(self):
		self.notice()
		length1 = len(self.note)
		length2 = len(self.inputs.split("\n")) - 1
		if length1 != length2: return ""
		if length1 == length2: return self.inputs
	def set_inputs(self, inputs):
		self.inputs = inputs
		return

	def get_helper(self):
		if self.result != "":
			self.result, data = "", self.result
			return data

		self.notice()
		length1 = len(self.note)
		length2 = len(self.inputs.split("\n")) - 1
		if self.status == 0: return ""
		if self.status == 1: self.status = 0; return self.note[length2]

	def server_writing(self):
		self.inputs = ""
		self.status = 0
		return

	def client_reading(self, data):
		action_signin = ["R", "L"]
		action_friend = ["F", "P", "A", "D"]
		if self.action in action_signin and self.inputs == "": self.username = data[:-1]
		if self.action in action_friend and self.inputs == "": self.peername = data[:-1]

		self.inputs += data
		self.status = 1
		return

	def server_reading(self, data):
		data = data.split("\n")

		info = [self.action, data[0], self.username, self.peername]
		if   self.action == "" : logging.info("[Action {}]".format(data[0]))
		elif self.action == "R": logging.info("[Action {}] **{}** \"{}\" register.".       format(*info[:-1]))
		elif self.action == "L": logging.info("[Action {}] **{}** \"{}\" login.".          format(*info[:-1]))
		elif self.action == "A": logging.info("[Action {}] **{}** \"{}\" create friendship \"{}\".".format(*info))
		elif self.action == "D": logging.info("[Action {}] **{}** \"{}\" remove friendship \"{}\".".format(*info))
		elif self.action == "P": logging.info("[Action {}] **{}** \"{}\" accept friendship \"{}\".".format(*info))
		elif self.action == "F": logging.info("[Action {}] **{}** \"{}\" get friend list.".format(*info[:-1]))
		else: logging.warning("{}: [Action {}] Not exists.".format(self.address, self.action))

		if   self.action == "": self.action = data[0]
		elif self.action != "" and data[0] == "Pass": self.action = ""
		
		action_friend = ["F", "P", "A", "D"]
		if self.action in action_friend: self.inputs = self.username + "\n"
		else: self.inputs = ""
		
		self.status = 1
		if len(data) != 1: self.result = '\n'.join(data[1:])
		return
