"""
This Module Is Used For Handling Notification
Regarding New Filtered Log
"""

import time
import logging
import sys
import requests
import src.db_

logger = logging.getLogger(__name__)

class Notif():
	"""
	Class For Store All Var and Method Used For Notified
	New Filtered Log
	"""

	def __init__(self, host):
		"""
		Initialization Notif Class
		"""

		self.host = host
		self.db_conn = src.db_.DB(self.host.replace('.','_'))


	def telegram_notif(self, token = '', chatid = ''):
		"""
		This method is used to send new filtered log to
		the telegram, via telegram bot
		"""

		try:
			logger.info("Send Notif To Telegram Bot (%s) (%s)", token, chatid)

			new_log = self.db_conn.get_new_log_tele()

			if len(new_log) != 0:
				for log in new_log:

					text = f" [!] {self.host} - {log[0]} \n\n [+] {' '.join(log[1:3])} \n [+] {log[3]} \n\n [=] {' '.join(log[4:])}"

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
						self.db_conn.insert_new_log_tele(log[0], ' '.join(log[1:]), 'SUCCESS')
						logger.info("Telegram Notif SUCCESS %s", log)
					else:
						self.db_conn.insert_new_log_tele(log[0], ' '.join(log[1:]), 'FAILED')
						logger.info("Telegram Notif FAILED %s", log)
			else:
				logger.info('Log For Sending To Telegram is 0 ... ABORTING')


		except Exception:
			logger.exception('TELEGRAM NOTIF ERROR')
			sys.exit(1)
