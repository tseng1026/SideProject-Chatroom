# coding='utf-8'

import socket
import sys
import logging
import threading

import client_action

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	host = str(sys.argv[1])
	port = int(sys.argv[2])

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))

	logging.info("    Connect to server on {} port {}.".format(host, port))
	logging.info("------------------- Client Log -------------------")

	action_sign = ["", "R", "L"]
	action_main = ["", "M", "F", "P", "A", "D"]
	worker = client_action.Action(sock)
	while True:
		status = worker.get_status()
		action = worker.get_action()

		if status == -1: break

		try:
			if (status == 1 and action not in action_sign) or \
			   (status == 3 and action not in action_main):
				worker.set_status(min(status // 2 * 2, 2))
				worker.set_action("")

			elif status == 0: worker.sign_menu()
			elif status == 1: worker.sign_exec()
			
			elif status == 2: worker.main_menu()
			elif status == 3: worker.main_friend_list()
			elif status == 4: worker.main_friend_exec()
			elif status == 5:
				rt = threading.Thread(target = worker.main_reading)
				wt = threading.Thread(target = worker.main_writing)

				rt.start()
				wt.start()

				rt.join()
				wt.join()

				### TODO: handle thread at the same time
		except:
			worker.set_status(-1)

	sock.close()