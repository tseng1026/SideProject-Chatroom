# coding='utf-8'

import socket
import logging
import database

class Action():
	def __init__(self, socket):
		self.socket  = socket
		self.address = socket.getpeername()

		self.action = ""
		self.result = ""

		self.username = ""
		self.peername = ""

	def get_action(self): return self.action
	def set_action(self, action):
		self.action = action
		return

	def get_result(self): return self.result
	def set_result(self, result):
		self.result = result
		return

	def client_reading(self, data):
		data = data.split("\n")

		self.result = "Fail"
		if   self.action == "": self.result = data[0]
		elif self.action == "R" and database.Account.insert(data[0], data[1], self.address): self.result = "Pass"
		elif self.action == "L" and database.Account.verify(data[0], data[1], self.address): self.result = "Pass"
		elif self.action == "A" and database.Friends.insert(data[0], data[1]): self.result = "Pass"
		elif self.action == "D" and database.Friends.delete(data[0], data[1]): self.result = "Pass"
		elif self.action == "P" and database.Friends.accept(data[0], data[1]): self.result = "Pass"
		elif self.action == "F":
			tmp1 = "Friend:  " + '\t'.join([item[0] for item in database.Friends.friend(data[0], 1)])
			tmp2 = "Pending: " + '\t'.join([item[0] for item in database.Friends.friend(data[0], 0)])
			if tmp1 != False and tmp2 != False: self.result = "Pass" + "\n" + tmp1 + "\n" + tmp2 + "\n"

		action_signin = ["R", "L"]
		action_friend = ["F", "P", "A", "D"]
		if self.action in action_signin and self.result == "Pass": self.username = data[0]
		if self.action in action_friend and self.result == "Pass": self.peername = data[1]
		return
		
	def client_writing(self):
		info = [self.address, self.action, self.result[:4], self.username, self.peername]
		if   self.action == "" : logging.info("{}: [Action {}]".format(self.address, self.result))
		elif self.action == "R": logging.info("{}: [Action {}] **{}** \"{}\" register.".       format(*info[:-1]))
		elif self.action == "L": logging.info("{}: [Action {}] **{}** \"{}\" login.".          format(*info[:-1]))
		elif self.action == "A": logging.info("{}: [Action {}] **{}** \"{}\" create friendship \"{}\".".format(*info))
		elif self.action == "D": logging.info("{}: [Action {}] **{}** \"{}\" remove friendship \"{}\".".format(*info))
		elif self.action == "P": logging.info("{}: [Action {}] **{}** \"{}\" accept friendship \"{}\".".format(*info))
		elif self.action == "F": logging.info("{}: [Action {}] **{}** \"{}\" get friend list.".format(*info[:-1]))
		else: logging.warning("{}: [Action {}] Not exists.".format(self.address, self.action))

		if   self.action == "": self.action = self.result
		elif self.action != "" and self.result[:4] == "Pass": self.action = ""
		self.result = ""
		return
