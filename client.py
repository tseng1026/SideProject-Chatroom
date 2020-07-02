# coding='utf-8'

import select
import socket
import sys
import logging

import client_action

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	host = str(sys.argv[1])
	port = int(sys.argv[2])

	# Create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((host, port))

	logging.info("    Connect to server on {} port {}.".format(host, port))
	logging.info("------------------- Client Log -------------------")

	socket_list = [server]

	action_sign = ["", "R", "L"]
	action_main = ["", "M", "F", "P", "A", "D"]
	worker = client_action.Action(server)
	
	while True:
		readable, writable, exceptional = select.select(socket_list + [sys.stdin], socket_list + [sys.stdout], socket_list, 5)

		for sock in writable:
			try:
				data = ""
				if sock is server    : data = worker.get_inputs()
				if sock is sys.stdout: data = worker.get_helper()

				if data == ""  : continue

				if sock is server:     sock.send(data[:-1].encode())
				if sock is sys.stdout: sys.stdout.write(data); sys.stdout.flush()

				if sock is server: worker.server_writing()
				k += 1
			except:
				pass

		for sock in readable:
			try:
				if sock is server   : data = sock.recv(1024).decode()
				if sock is sys.stdin: data = sys.stdin.readline()

				if data == ""  : continue
				if data == "q!": worker.set_action(""); continue
				
				if sock is server   : worker.server_reading(data)
				if sock is sys.stdin: worker.client_reading(data)

			except:
				pass
	sock.close()