"""
This module is used to parsing telegram log
based on given word pattern, and then
send filtered log to the telegram

created by berrabe
"""

import sys
import os
import logging
import datetime
import paramiko
import src.db_

logger = logging.getLogger(__name__)

class MikrotikLogger():
	"""
	Class Mikrotik Logger
	"""

	def __init__(self, pattern = None, host = "192.168.1.1", port = "22", username = "admin", password = ""):
		"""
		Constructor Class MikrotikLogger,
		when make object form MikrotikClass,
		must provide a list of patterns
		so that the log can be filtered
		"""
		if not os.path.exists('logs'):
			logger.info("Logs Folder Not Exist, Creating")
			os.makedirs('logs')

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
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.date = datetime.datetime.now().strftime("%d-%b-%y")

		self.db_conn = src.db_.DB(self.host.replace('.','_'))
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

			logger.info("SSH => Get Log File")
			sftp = ssh.open_sftp()
			sftp.get('PythonMikrotikLogger.0.txt',f"./logs/log__{self.date}__{self.host}")
			sftp.close()

			log_file = open(f"./logs/log__{self.date}__{self.host}",'r')
			logs = log_file.readlines()
			log_file.close()

			logger.info("SSH => Success")

			return logs

		except Exception:
			logger.exception("SSH TO MIKROTIK ERROR")
			sys.exit(1)


	def __filtering(self):
		"""
		This method is useful filtering log basend given pattern.
		All logs that are filtered will be stored in variables
		self.filtered_log
		"""

		try:
			start = 0
			logs = self.__ssh()
			session = self.db_conn.get_last_session()

			for log in logs:
				if session == log.split() and session != 'none':
					logger.info("Raw Log and Sesion Log Match, Start Filtering New Log From Last Session")
					start = 1
					continue

				if session == 'none' or start == 1:
					for pattern in self.patterns:
						if '-' in pattern.split():
							if ' '.join(pattern.split()[1:]) in log[:]:
								logger.info("Got - (%s) Pattern", ' '.join(pattern.split()[1:]))
								break
						elif '+' in pattern.split():
							if ' '.join(pattern.split()[1:]) in log[:]:
								self.filtered_log.append(log.split())
								logger.info("Got + (%s) Pattern", ' '.join(pattern.split()[1:]))
								break
						else:
							logger.warning("There is some unknown symbol on pattern - !! (%s)", pattern)
							continue
				else:
					continue

			if len(self.filtered_log) != 0:

				logger.info("Got (%s) New Record", len(self.filtered_log))

				self.db_conn.insert_filtered_log(self.filtered_log)

			else:
				logger.info("No New Log Detected")

			sess_buff = logs[-1].split()
			logger.info("Last Record On (%s)", ' '.join(sess_buff))
			self.db_conn.insert_latest_session(sess_buff)

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
