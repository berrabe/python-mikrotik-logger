"""
python mikrotik logger

read the docs :
- https://github.com/berrabe/python-mikrotik-logger.git

created by berrabe
"""

import logging
import sys
import yaml
from src import mikrotik_

if __name__ == '__main__':
	try:
		logging.basicConfig(
			level = logging.INFO,
			# filename='python-mikrotik-logger.log', filemode='a',
			format = '[ %(levelname)s ] [ %(name)s ] [ %(asctime)s ] => %(message)s',
			datefmt='%d-%b-%y %H:%M:%S'
			)


		with open('hosts.yml') as yaml_:
			conf = yaml.load(yaml_, Loader=yaml.FullLoader).get('mtk_devices')
			hosts = conf['hosts']
			patterns = conf['patterns']
			var = conf['vars']


		obj = mikrotik_.MikrotikLogger(pattern = patterns)


		for host in hosts.keys():

			obj.start(
				host = hosts[host]['mtk_host'],
				port = hosts[host]['mtk_port'],
				username = hosts[host]['mtk_username'],
				password = hosts[host]['mtk_password']
				)

			obj.notif_telegram(
				token = var['telegram_token'],
				chatid = var['telegran_chatid'])

			obj.show()

	except KeyboardInterrupt:
		sys.exit(17)
