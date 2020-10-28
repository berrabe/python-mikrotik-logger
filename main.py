"""
python mikrotik logger

read the docs :
- https://github.com/berrabe/python-mikrotik-logger.git

created by berrabe
"""

import logging
import sys
from src import mikrotik_

if __name__ == '__main__':
	try:
		logging.basicConfig(
			level = logging.INFO,
			# filename='python-mikrotik-logger.log', filemode='a',
			format = '[ %(levelname)s ] [ %(name)s ] [ %(asctime)s ] => %(message)s',
			datefmt='%d-%b-%y %H:%M:%S'
			)

		obj = mikrotik_.MikrotikLogger(pattern = [
			'- hotspot',
			'+ error',
			'+ logged',
			'+ warning',
			'+ down',
			'+ rebooted',
			'+ critical',
			'+ failure',
			])

		obj.start(
			host = "YOUR MIKROTIK IP",
			port = 22,
			username = "YOUR MIKROTIK USER",
			password = "YOUR MIKROTIK PASSWORD"
			)

		obj.show()
		obj.notif_telegram(
			token = 'YOUR TELEGRAM BOT TOKEN',
			chatid = 'YOUR TELEGRAM CHATID')

	except KeyboardInterrupt:
		sys.exit(17)
