# coding='utf-8'

import socket
import sys
import time
import logging
import threading
from getpass import getpass

def reading(sock):
	addr = sock.getsockname()
	
	while True:
		data = sock.recv(1024).decode()
		if not data: continue

		sendname, message = data.split(" ", 1)
		logging.info("Message received from {}.".format(sendname))


def writing(sock):
	addr = sock.getsockname()
	
	while True:
		recvname, message = input(), input()
		data = recvname + " " + message
		sock.send(data.encode())
		logging.info("Message sent to {}.".format(recvname))

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	host = str(sys.argv[1])
	port = int(sys.argv[2])

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))

	logging.info("    Connect to server on {} port {}.".format(host, port))
	logging.info("------------------- Client Log -------------------")

	sock.send(input  ("Username: ").encode())
	sock.send(getpass("Password: ").encode())


	rt = threading.Thread(target = reading, args = (sock, ))
	wt = threading.Thread(target = writing, args = (sock, ))

	rt.start()
	wt.start()

	rt.join()
	wt.join()