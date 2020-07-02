# coding='utf-8'

import select
import socket
import sys
import logging

import database
import server_action

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	database.Account()
	database.Friends()
	database.Message()

	host = str(sys.argv[1])
	port = int(sys.argv[2])

	# create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)

	# bind the socket to the port
	server.bind((host, port))
	server.listen(5)

	logging.info("Start up server on {} port {}.".format(host, port).center(50))
	logging.info("------------------- Server Log -------------------")

	# sockets to read and write
	socket_list = []

	worker = {}
	

	while True:
		# readable , writable , exceptional = select.select(sockR, sockW, sockR, timeout)
		readable, writable, exceptional = select.select(socket_list + [server], socket_list, socket_list + [server])

		for sock in readable:
			# change the connection to client channel
			if sock is server:
				sock.setblocking(0)

				conn, addr = sock.accept()
				socket_list.append(conn)
				
				worker[addr] = server_action.Action(conn)
				logging.info("{}: Connection created.".format(addr))
				continue

			try:
				addr = sock.getpeername()
				data = sock.recv(1024).decode()
				
				# if data == ""  : worker[addr].set_status(-1); continue
				if data == ""  : continue
				if data == "q!": worker[addr].set_action(""); continue
				worker[addr].client_reading(data)

			except:
				pass
			

		for sock in writable:
			try:
				addr = sock.getpeername()
				data = worker[addr].get_result()

				if data == ""  : continue
				sock.send(data.encode())
				worker[addr].client_writing()

			except:
				pass
			# try:
			# 	if status == -1: 
			# 		socket_list.remove(sock)
			# 		readable.   remove(sock)
			# 		writable.   remove(sock)
			# 		del worker[addr]
					
			# 		logging.info("{}: **Done** Connection closed.".format(addr))
			# 		continue
			# except:
			# 	pass

