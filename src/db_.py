"""
This Module Is Used For Handling Database
Separately From Main Module
"""

import sqlite3
import logging
import sys

logger = logging.getLogger(__name__)

class DB():
	"""
	Main Class On This Module
	"""

	def __init__(self, db_table):
		"""
		Initialization Database
		"""

		self.conn = sqlite3.connect('logs.db')
		self.curr = self.conn.cursor()
		self.db_table = db_table

		self.curr.execute(f"""CREATE TABLE IF NOT EXISTS '{self.db_table}_logs' (
		ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		DATE TEXT NULL,
		TIME TEXT NOT NULL,
		CATEGORY TEXT NOT NULL,
		LOG TEXT NOT NULL
		)
		""")

		self.curr.execute(f"""CREATE TABLE IF NOT EXISTS '{self.db_table}_session' (
		ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		DATE TEXT NULL,
		TIME TEXT NOT NULL,
		CATEGORY TEXT NOT NULL,
		LOG TEXT NOT NULL
		)
		""")

		self.curr.execute(f"""CREATE TABLE IF NOT EXISTS '{self.db_table}_notif_tele' (
		ID INTEGER NOT NULL PRIMARY KEY,
		LOG TEXT NOT NULL,
		STATUS TEXT NOT NULL
		)
		""")


	def get_last_session(self):
		"""
		This method is useful for detect the last session from
		SQLite Database ... this method very important for
		method filtering
		"""

		try:
			self.curr.execute(f"SELECT * FROM '{self.db_table}_session' ORDER BY ID DESC LIMIT 1")
			data = self.curr.fetchone()

			if data is None:
				logger.info("Session Log Does Not Exist, Start Filtering New Log From Beginning")
			else:
				logger.info("Session Log Exist")
				return ' '.join(data[1:]).split()

			return 'none'

		except Exception:
			logger.exception("GATHER SESSION FAILED")
			sys.exit(1)


	def insert_filtered_log(self, filtered_log):
		"""
		This method is used to send filtered log to
		the SQLite 3 Database, but before that, it
		will filter if new log from filter is already
		in database or not
		"""

		try:
			if len(filtered_log) != 0:
				logger.info("Checking Database Record, Prevent Duplication")
				self.curr.execute(f"SELECT TIME,CATEGORY,LOG FROM '{self.db_table}_logs'")
				db_data = self.curr.fetchall()

				for item in filtered_log:
					item.insert(3, ' '.join(item[3:]))
					del item[4:]

					if tuple(item)[1:] not in db_data:
						logger.info("Sending To Database (%s)", item)
						self.curr.execute(f"INSERT INTO '{self.db_table}_logs' VALUES (NULL, :date, :time, :cat, :log)",
							{'date' : item[0], 'time' : item[1], 'cat' : item[2], 'log' : " ".join(item[3:])})
					else:
						logger.info("Record (%s) Already In Database", item)

				self.conn.commit()


			else:
				logger.info("Empty Log, Abort Sending Database")

		except Exception:
			logger.exception('INSERT FILTERED LOG ERROR')
			sys.exit(1)


	def insert_latest_session(self, sess_buff):
		"""
		This method is used to send latest gathered
		log from mikrotik device to session db table
		"""

		try:
			self.curr.execute(f"INSERT INTO '{self.db_table}_session' VALUES (NULL, :date, :time, :cat, :log)",
			{'date' : sess_buff[0], 'time' : sess_buff[1], 'cat' : sess_buff[2], 'log' : " ".join(sess_buff[3:])})

			self.conn.commit()
			logger.info("Insert Latest Record to DB For Session")

		except Exception:
			logger.exception('SENDING LATEST SESSION ERROR')
			sys.exit(1)


	def get_new_log_tele(self):
		"""
		This method is used to get new filtered log
		that have not been sended to telegram with
		sql join
		"""

		try:
			self.curr.execute(f"""
				SELECT '{self.db_table}_logs'.ID, '{self.db_table}_logs'.DATE, '{self.db_table}_logs'.TIME, '{self.db_table}_logs'.CATEGORY, '{self.db_table}_logs'.LOG
				FROM '{self.db_table}_logs' 
				LEFT JOIN '{self.db_table}_notif_tele' 
				ON '{self.db_table}_logs'.ID = '{self.db_table}_notif_tele'.ID
				WHERE '{self.db_table}_notif_tele'.STATUS IS NULL
				""")
			data = self.curr.fetchall()

			logger.info("Get New Filtered Log For Sending to Telegram SUCCESS, Total (%s) New Log(s)", len(data))
			return data

		except Exception:
			logger.exception('GET NEW LOG FOR NOTIFIED TELEGRAM ERROR')
			sys.exit(1)


	def insert_new_log_tele(self, id_, log, status):
		"""
		This method is used to insert status for
		telegram notif
		"""

		try:
			self.curr.execute(f"INSERT INTO '{self.db_table}_notif_tele' VALUES (:id, :log, :status)",
			{'id' : id_, 'log' : log, 'status' : status})

			self.conn.commit()
			logger.info("Update Telegram Status For ID (%s) to DB", id_)

		except Exception:
			logger.exception('INSERT NEW LOG FOR TELEGRAM ERROR')
			sys.exit(1)
