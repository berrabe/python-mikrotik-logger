from src import *
import logging
import sys

if __name__ == '__main__':
	try:
		logging.basicConfig(
			level = logging.INFO, 
			filename='mikrotik.log', filemode='a',
			format = '[ %(levelname)s ] [ %(name)s ] [ %(asctime)s ] => %(message)s', 
			datefmt='%d-%b-%y %H:%M:%S'
			)

		obj=mikrotik_.mikrotik_(pattern = [
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