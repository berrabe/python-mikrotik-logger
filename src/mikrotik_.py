"""
This module is used to parsing telegram log
based on given word pattern, and then
send filtered log to the telegram

created by berrabe
"""

import time
import os.path
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

		logger.info("Initialization Pattern Success")

		if pattern is None:
			pattern = [
			'+ critical',
			'+ down',
			'+ error',
			'+ warning',
			'+ rebooted',
			'+ failure'
			]

		self.list_all = []
		self.filtered_log = []
		self.patterns = pattern
		self.host = "192.168.1.1"
		self.port = 22
		self.username = "admin"
		self.password = ""


	def start(self, host, port, username, password):
		"""
		This method is useful for running log filtering
		based on given pattern. You must overrides hardcoded
		variables on method constructor associated with mikrotik
		login / ssh credential
		"""

		logger.info("Initialization Mikrotik Credential Success")

		self.host = host
		self.port = port
		self.username = username
		self.password = password

		self.__filtering()


	def __ssh(self):
		"""
		This method is useful for retrieving logs from MikroTik
		device using ssh protocol
		"""

		logger.info("SSH to Mikrotik Device")

		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(self.host, self.port, self.username, self.password, look_for_keys=False)
			stdin, stdout, stderr = ssh.exec_command("/log print")

			logger.info("SSH Success")

			return stdout.readlines()

		except Exception:
			logger.exception("SSH TO MIKROTIK ERROR")


	def __filtering(self):
		"""
		This method is useful filtering log basend given pattern.
		All logs that are filtered will be stored in variables
		self.filtered_log
		"""

		try:
			start = 0
			logs = self.__ssh()

			if os.path.exists('.__last_sessions__'):
				logger.info("Session File Exist, Starting From Session")
				file_open = open('.__last_sessions__','r')
				session_file = file_open.readlines()[0]
			else:
				session_file = 'none'
				logger.info("Session File Not Exist, Starting From Beginning")

			logger.info("Ready For Filtering Log Based Given Pattern")

			for log in logs:
				if session_file == str(log.split()) and session_file != 'none':
					logger.info("Filtering Mikrotik Log From Session")
					start = 1
					continue

				if session_file == 'none' or start == 1:
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

				last_session = open('.__last_sessions__','w+')
				last_session.write(str(self.filtered_log[-1]))
				last_session.close()
			else:
				logger.info("No New Log Detected")

		except Exception:
			logger.exception("FILTERING LOG ERROR")


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
					if len(item[0].split(':')) == 3:
						logger.info("Current Log Does Not Have Date, Send Format 1")
						text = f" [!] {self.host} \n\n [+] {item[0]} \n [+] {item[1]} \n\n [=] {' '.join(item[2:])}"
					else:
						logger.info("Current Log Have Date In It, Send Format 2")
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
