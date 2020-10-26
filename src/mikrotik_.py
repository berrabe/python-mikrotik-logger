import time
import paramiko
import logging
import re
import os.path
import requests

logger = logging.getLogger(__name__)

class mikrotik_():
	"""docstring for mikrotik"""

	def __init__(self, pattern=[], neg=[]):
		logger.info("Initialization Pattern Success")
		self.list_all = []
		self.filtered_log = []
		self.pattern = pattern
		self.neg = neg

	def start(self, host="192.168.1.1", port=22, username="admin", password=""):
		logger.info("Initialization Mikrotik Credential Success")
		self.host = host
		self.port = port
		self.username = username
		self.password = password

		self.filtering()

	def __ssh(self):
		try:
			logger.info("SSH to Mikrotik Device")
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(self.host, self.port, self.username, self.password, look_for_keys=False)

			stdin, stdout, stderr = ssh.exec_command("/log print")
			logger.info("SSH Success")
			return stdout.readlines()

		except Exception as e:
			logger.exception("SSH TO MIKROTIK ERROR")

	def filtering(self):
		try:
			start = 0
			lines = self.__ssh()

			if os.path.exists('./.__last_sessions__'):
				logger.info("Session File Exist, Starting From Session")
				f = open('.__last_sessions__','r')
				session_file = f.readlines()[0]
			else:
				session_file = 'none'
				logger.info("Session File Not Exist, Starting From Beginning")

			logger.info("Ready For Filtering Log Based Given Pattern")
		
			for x in lines:
				if session_file == str(x.split()) and session_file != 'none':
					logger.info("Filtering Mikrotik Log From Session")
					start = 1
					continue

				if session_file == 'none' or start == 1:
					for y in self.pattern:
						if '-' in y.split():
							if y.split()[1] in x[:]:
								break
						elif '+' in y.split():
							if y.split()[1] in x[:]:
								self.filtered_log.append(x.split())
								break
						else:
							logger.warning(f"There is some unknown symbol on pattern - !! ({y})")
							continue
				else:
					continue

			if len(self.filtered_log) != 0:
				logger.info(f"Got {len(self.filtered_log)} New Record")
				logger.info(f"Last Record On {self.filtered_log[-1]}")
				last_session = open('.__last_sessions__','w+')
				last_session.write(str(self.filtered_log[-1]))
				last_session.close()
			else:
				logger.info("No New Log Detected")

		except Exception as e:
			logger.exception("FILTERING LOG ERROR")

	def show(self):
		if len(self.filtered_log) != 0:
			[ print(x[:]) for x in self.filtered_log ]

	def notif_telegram(self, token = '', chatid = ''):
		try:
			if len(self.filtered_log) != 0:
				for item in self.filtered_log:

					logger.info(f"Send Notif To Telegram Bot - {token}")
					if len(item[0].split(':')) == 3:
						logger.info("Current Log Does Not Have Date, Send Format 1")
						text = f" [!] {self.host} \n\n [+] {item[0]} \n [+] {item[1]} \n\n [=] {' '.join(item[2:])}"
					else:
						logger.info("Current Log Have Date In It, Send Format 2")
						text = f" [!] {self.host} \n\n [+] {' '.join(item[0:2])} \n [+] {item[2]} \n\n [=] {' '.join(item[3:])}"

					data = {
						"chat_id" : f"{chatid}",
						"text" : f"<code>{text}</code>",
						"parse_mode" : "html"
					}
			
					req_ = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data = data, timeout = 3)
					if req_.status_code == 200:
						logger.info(f"Telegram Notif Success {req_.status_code} - {chatid}")
					else:
						logger.info(f"Telegram Notif Failed {req_.status_code} - {chatid}")
			else:
				logger.info("Empty Log, Abort Sending Notif")

		except Exception as e:
			logger.exception('Telegram Notif Error')
