# coding='utf-8'

import select
import socket
import os
import sys
import queue
import logging

userlist = {}

def conversion(tag, convert_type):
	return userlist[tag]

def login(sock, loginstate):
	addr = sock.getpeername()
	if loginstate[addr][0] == 2: return True
	
	info = sock.recv(1024).decode()
	if not info: return False

	user = ""
	flag = loginstate[addr][0] + 1
	if flag == 1: user = info
	if flag != 1: user = loginstate[addr][1]
	loginstate[addr] = (flag, user)
	## TODO: connect to db, check if correct

	userlist[addr] = user
	userlist[user] = addr
	return False

def reading(sock, processing_queue):
	sendaddr = sock.getpeername()

	# receive from sender
	data = sock.recv(1024).decode()
	if not data: return

	# server processing
	recvname, message = data.split(" ", 1)
	recvaddr = conversion(recvname, 1)

	if recvaddr not in processing_queue: processing_queue[recvaddr] = queue.Queue()
	processing_queue[recvaddr].put((sendaddr, message))
	logging.info("Message recv from {} to {}.".format(sendaddr[1], recvaddr[1]))
	return

def writing(sock, processing_queue):
	recvaddr = sock.getpeername()

	# server processing
	if recvaddr not in processing_queue: return
	sendaddr, message = processing_queue[recvaddr].get()
	sendname = conversion(sendaddr, 0)

	# send to receiver
	data = sendname + " " + message
	sock.send(data.encode())
	logging.info("Message sent from {} to {}.".format(sendaddr[1], recvaddr[1]))

	# delete processing_queue
	if processing_queue[recvaddr].empty():
		del processing_queue[recvaddr]
	return

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	host = str(sys.argv[1])
	port = int(sys.argv[2])

	# create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)

	# bind the socket to the port
	server.bind((host, port))
	server.listen(5)

	logging.info("      Start up server on {} port {}.".format(host, port))
	logging.info("------------------- Server Log -------------------")

	# sockets to read and write
	sockR = [server]
	sockW = []

	loginstate = {}
	processing_queue = {}

	while True:
		# readable , writable , exceptional = select.select(sockR, sockW, sockR, timeout)
		readable, writable, exceptional = select.select(sockR, sockW, sockR)

		for sock in readable:
			# change the connection to client channel
			if sock is server:
				sock.setblocking(0)

				conn, addr = sock.accept()
				sockR.append(conn)
				sockW.append(conn)
				
				loginstate[addr] = (0, "")
				logging.info("Connection created.".format(addr))
				continue

			# processing login request
			check = login(sock, loginstate)
			if not check: continue
			
			# processing reading request
			reading(sock, processing_queue)


		for sock in writable:
			# processing writing request
			writing(sock, processing_queue)