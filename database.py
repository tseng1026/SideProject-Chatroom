import sqlite3
import logging

class Account():
	def __init__(self):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS ACCOUNT
							 (USER		text PRIMARY KEY NOT NULL UNIQUE,
							  PSWD		text NOT NULL,
							  STATUS	int  NOT NULL,
							  ADDR		text NOT NULL);''')
			db.commit()
			logging.info("Successfully create server.db - account.".center(50))

	@staticmethod
	def exists(username):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute("SELECT COUNT(*) FROM ACCOUNT WHERE USER = ?", [username])
			
			result = cursor.fetchone()
			return bool(result[0])

	@staticmethod
	def status(username):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username): return -1
			var = [username]
			cursor.execute("SELECT STATUS FROM ACCOUNT WHERE USER = ?", var)
			
			result = cursor.fetchone()
			return result[0]
		return -1

	@staticmethod
	def insert(username, password, address):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if Account.exists(username): return False
			var = [username, password, 1, str(address)]
			cursor.execute("INSERT INTO ACCOUNT (USER, PSWD, STATUS, ADDR) VALUES (?, ?, ?, ?)", var)

			db.commit()
			return True
		return False

	@staticmethod
	def verify(username, password, address):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username): return False
			var = [username, password]
			cursor.execute("SELECT * FROM ACCOUNT WHERE USER = ? AND PSWD = ?", var)
			result = cursor.fetchall()
			if len(result) == 0: return False
			
			cursor.execute("UPDATE ACCOUNT SET STATUS = 1 WHERE USER = ? AND PSWD = ?", var)
			cursor.execute("UPDATE ACCOUNT SET ADDR = ?   WHERE USER = ? AND PSWD = ?", [str(address)] + var)

			db.commit()
			return True
		return False

	@staticmethod
	def change(identity, tag):
		# tag == 0: name -> addr
		# tag == 1: addr -> name
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if tag == 0: cursor.execute("SELECT ADDR FROM ACCOUNT WHERE USER = ?", [str(identity)])
			if tag == 1: cursor.execute("SELECT USER FROM ACCOUNT WHERE ADDR = ?", [str(identity)])
			result = cursor.fetchone()[0]

			if tag == 0:
				result = result[1:-1]
				result = result.split(", ")
				result = (result[0][1:-1], int(result[1]))
			return result


class Friends():
	def __init__(self):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS FRIENDS
							 (USER1		text NOT NULL,
							  USER2		text NOT NULL,
							  STATUS	int  NOT NULL);''')
			db.commit()
			logging.info("Successfully create server.db - friends.".center(50))

	@staticmethod
	def exists(username1, username2):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute("SELECT COUNT(*) FROM FRIENDS WHERE USER1 = ? AND USER2 = ?", [username1, username2])
			
			result = cursor.fetchone()
			return bool(result[0])

	@staticmethod
	def friend(username, status):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username): return False
			var = [username, status]
			cursor.execute("SELECT USER2 FROM FRIENDS WHERE USER1 = ? AND STATUS = ?", var)

			result = cursor.fetchall()
			if len(result) == 0: return [(" ", )]
			if len(result) != 0: return result
		return False

	@staticmethod
	def insert(username1, username2):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username1): return False
			if not Account.exists(username2): return False
			if Friends.exists(username1, username2): return False
			if Friends.exists(username2, username1): return False

			var = [username1, username2, 0]
			cursor.execute("INSERT INTO FRIENDS (USER1, USER2, STATUS) VALUES (?, ?, ?)", var)
			db.commit()
			return True
		return False

	@staticmethod
	def accept(username1, username2):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username1): return False
			if not Account.exists(username2): return False
			if not Friends.exists(username1, username2) and \
			   not Friends.exists(username2, username1): return False

			var = []
			if Friends.exists(username1, username2): var = [username1, username2]
			if Friends.exists(username2, username1): var = [username2, username1]
			cursor.execute("UPDATE FRIENDS SET STATUS = 1 WHERE USER1 = ? AND USER2 = ?", var)

			db.commit()
			return True
		return False

	@staticmethod
	def delete(username1, username2):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(username1): return False
			if not Account.exists(username2): return False
			if not Friends.exists(username1, username2) and \
			   not Friends.exists(username2, username1): return False

			var = []
			if Friends.exists(username1, username2): var = [username1, username2]
			if Friends.exists(username2, username1): var = [username2, username1]
			cursor.execute("DELETE from FRIENDS where USER1 = ? AND USER2 = ?", var)

			db.commit()
			return True
		return False


class Message():
	def __init__(self):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS MESSAGE
							 (SEND		text NOT NULL,
							  RECV		text NOT NULL,
							  CONTENT	text NOT NULL);''')
			db.commit()
			logging.info("Successfully create server.db - message.".center(50))

	@staticmethod
	def exists(sendname, recvname):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()
			cursor.execute("SELECT COUNT(*) FROM MESSAGE WHERE SEND = ? AND RECV = ?", [sendname, recvname])
			
			result = cursor.fetchone()
			return bool(result[0])

	@staticmethod
	def insert(sendname, recvname, content):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(sendname): return False
			if not Account.exists(recvname): return False
			if not Friends.exists(sendname, recvname) and \
			   not Friends.exists(sendname, recvname): return False
			
			var = [sendname, recvname, content]
			cursor.execute("INSERT INTO MESSAGE (SEND, RECV, CONTENT) VALUES (?, ?, ?)", var)

			db.commit()
			return True
		return False

	@staticmethod
	def delete(sendname, recvname):
		with sqlite3.connect("server.db") as db:
			cursor = db.cursor()

			if not Account.exists(sendname): return False
			if not Account.exists(recvname): return False
			if not Message.exists(sendname, recvname): return False

			var = [sendname, recvname]
			cursor.execute("SELECT * FROM MESSAGE WHERE SEND = ? AND RECV = ?", var)
			result = cursor.fetchone()
			if len(result) == 0: return False

			cursor.execute("DELETE from MESSAGE where SEND = ? AND RECV = ? AND CONTENT = ?", var + [result[2]])
			db.commit()
			return result[2]
		return False