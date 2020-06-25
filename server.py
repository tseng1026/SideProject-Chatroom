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
	action_sign = ["", "R", "L"]
	action_main = ["", "M", "F", "P", "A", "D"]

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


			# processing login request
			addr = sock.getpeername()

			status = worker[addr].get_status()
			action = worker[addr].get_action()

			try:
				if status == -1: 
					socket_list.remove(sock)
					readable.   remove(sock)
					writable.   remove(sock)
					del worker[addr]

					logging.info("{}: Connection closed.".format(addr))
					continue
			except:
				pass
			
			try:
				if (status == 1 and action not in action_sign) or \
				   (status == 3 and action not in action_main):
					worker[addr].set_status(min(status // 2 * 2, 2))
					worker[addr].set_action("")
					continue

				if status == 0: worker[addr].sign_menu()
				if status == 1: worker[addr].sign_exec()
				if status == 2: worker[addr].main_menu()
				if status == 4: worker[addr].main_friend_exec()
				if status == 5: worker[addr].main_reading()
			
			except:
				worker[addr].set_status(-1)

		for sock in writable:
			addr = sock.getpeername()

			status = worker[addr].get_status()
			action = worker[addr].get_action()

			try:
				if status == -1: 
					socket_list.remove(sock)
					readable.   remove(sock)
					writable.   remove(sock)
					del worker[addr]
					
					logging.info("{}: Connection closed.".format(addr))
					continue
			except:
				pass

			try:
				if status == 3: worker[addr].main_friend_list()
				if status == 5: worker[addr].main_writing()

			except:
				worker[addr].set_status(-1)