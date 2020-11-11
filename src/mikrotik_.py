"""
This module is used to parsing telegram log
based on given word pattern, and then
send filtered log to the telegram

created by berrabe
"""

import time
import sys
import sqlite3
import logging
import paramiko
import requests

logger = logging.getLogger(__name__)

class MikrotikLogger():
	"""
	Class Mikrotik Logger
	"""

	def __init__(self, pattern = None):
		"""
		Constructor Class MikrotikLogger,
		when make object form MikrotikClass,
		must provide a list of patterns
		so that the log can be filtered
		"""

		if pattern is None:
			pattern = [
			'+ critical',
			'+ down',
			'+ error',
			'+ warning',
			'+ rebooted',
			'+ failure'
			]

		self.filtered_log = []
		self.patterns = pattern
		self.host = "192.168.1.1"
		self.port = 22
		self.username = "admin"
		self.password = ""
		self.date = None

		self.conn = sqlite3.connect('logs.db')
		self.curr = self.conn.cursor()
		self.db_table = "192_168_1_1"


	def start(self, host, port, username, password):
		"""
		This method is useful for running log filtering
		based on given pattern. You must overrides hardcoded
		variables on method constructor associated with mikrotik
		login / ssh credential
		"""

		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.db_table = self.host.replace('.','_')

		self.curr.execute(f"""CREATE TABLE IF NOT EXISTS '{self.db_table}' (
		ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		DATE TEXT NULL,
		TIME TEXT NOT NULL,
		CATEGORY TEXT NOT NULL,
		LOG TEXT NOT NULL
		)
		""")

		self.__filtering()


	def __ssh(self):
		"""
		This method is useful for retrieving logs from MikroTik
		device using ssh protocol
		"""

		logger.info("SSH - (%s)", self.host)

		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(self.host, self.port, self.username, self.password, look_for_keys=False)

			logger.info("SSH => Get Current Date")
			stdin, date, stderr = ssh.exec_command(":put [/system clock get date]")

			date = [i.split('/') for i in date.readlines()]
			self.date = '/'.join(date[0][:2])

			logger.info("SSH => Get Log File")
			stdin, log, stderr = ssh.exec_command("/log print")

			logger.info("SSH => Success")

			return log.readlines()

		except Exception:
			logger.exception("SSH TO MIKROTIK ERROR")
			sys.exit(1)


	def __add_log_date(self, logs):
		"""
		This method is useful for add date to raw_logs ...
		cause mikrotik not included date when log in current day
		"""

		parse_log = []

		try:
			if len(logs) != 0:

				for item in logs[:-1]:
					item = item.split()

					if len(item[0].split(':')) == 3:
						item.insert(0, self.date)

					parse_log.append(' '.join(item))

			else:
				logger.info("Empty Log, Abort Sending Database")

			logger.info("Parsing Raw Log From (%s) - Success", self.host)
			return parse_log

		except Exception:
			logger.exception('Sending To Database Error')
			sys.exit(1)


	def __last_session(self):
		"""
		This method is useful for detect the last session from
		SQLite Database ... this method very important for
		method filtering
		"""

		try:
			self.curr.execute(f"SELECT * FROM '{self.db_table}' ORDER BY ID DESC" )
			data = self.curr.fetchone()

			if data is None:
				logger.info("Log Session Does Not Exist, Start Filtering New Log From Beginning")
			else:
				logger.info("Log Session Exist")
				return ' '.join(data[1:]).split()

			return 'none'

		except Exception:
			logger.exception("GATHER SESSION FAILED")
			sys.exit(1)


	def __filtering(self):
		"""
		This method is useful filtering log basend given pattern.
		All logs that are filtered will be stored in variables
		self.filtered_log
		"""

		try:
			start = 0
			raw_logs = self.__ssh()
			logs = self.__add_log_date(raw_logs)
			session = self.__last_session()

			for log in logs:
				if session == log.split() and session != 'none':
					logger.info("Raw Log and Sesion Log Match, Start Filtering New Log From Last Session")
					start = 1
					continue

				if session == 'none' or start == 1:
					for pattern in self.patterns:
						if '-' in pattern.split():
							if pattern.split()[1] in log[:]:
								logger.info("Got - (%s) Pattern", pattern.split()[1])
								break
						elif '+' in pattern.split():
							if pattern.split()[1] in log[:]:
								self.filtered_log.append(log.split())
								logger.info("Got + (%s) Pattern", pattern.split()[1])
								break
						else:
							logger.warning("There is some unknown symbol on pattern - !! (%s)", pattern)
							continue
				else:
					continue

			if len(self.filtered_log) != 0:

				logger.info("Got (%s) New Record", len(self.filtered_log))
				logger.info("Last Record On (%s)", self.filtered_log[-1])

				self.__db()

			else:
				logger.info("No New Log Detected")

		except Exception:
			logger.exception("FILTERING LOG ERROR")
			sys.exit(1)


	def show(self):
		"""
		This method is used to display all
		filtered logs to the terminal screen
		"""

		if len(self.filtered_log) != 0:
			# [ print(x[:]) for x in self.filtered_log ]
			for log in self.filtered_log:
				print(log[:])


	def notif_telegram(self, token = '', chatid = ''):
		"""
		This method is used to send new filtered log to
		the telegram, via telegram bot

		2 modes of delivery:

		First, delivery because
		it has no date, only time

		second, the shipment that has a date,
		because the log occurred not on that day, but already ...
		the format of mikrotik
		"""

		try:
			if len(self.filtered_log) != 0:
				for item in self.filtered_log:

					logger.info("Send Notif To Telegram Bot (%s)", token)
					date = ' '.join(item[0:2])
					text = f" [!] {self.host} \n\n [+] {date} \n [+] {item[2]} \n\n [=] {' '.join(item[3:])}"

					data = {
						"chat_id" : f"{chatid}",
						"text" : f"<code>{text}</code>",
						"parse_mode" : "html"
					}

					time.sleep(2)

					req_ = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
						data = data,
						timeout = 10)

					if req_.status_code == 200:
						logger.info("Telegram Notif SUCCESS (%s) - (%s)", req_.status_code, chatid)
					else:
						logger.info("Telegram Notif FAILED (%s) - (%s)", req_.status_code, chatid)
			else:
				logger.info("Empty Log, Abort Sending Notif")

		except Exception:
			logger.exception('Telegram Notif Error')
			sys.exit(1)



	def __db(self):
		"""
		This method is used to send filtered log to
		the SQLite 3 Database
		"""

		try:
			if len(self.filtered_log) != 0:
				logger.info("Sending To Database")

				for item in self.filtered_log:

					self.curr.execute(f"INSERT INTO '{self.db_table}' VALUES (NULL, :date, :time, :cat, :log)",
						{'date' : item[0], 'time' : item[1], 'cat' : item[2], 'log' : " ".join(item[3:])})

				self.conn.commit()


			else:
				logger.info("Empty Log, Abort Sending Database")

		except Exception:
			logger.exception('Sending To Database Error')
			sys.exit(1)
