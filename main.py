"""
python mikrotik logger

read the docs :
- https://github.com/berrabe/python-mikrotik-logger.git

created by berrabe
"""

import time
import logging
import sys
import yaml
from src import mikrotik_, notif_

logger = logging.getLogger(__name__)

if __name__ == '__main__':
	try:
		logging.basicConfig(
			level = logging.INFO,
			filename='python-mikrotik-logger.log', filemode='a',
			format = '[ %(levelname)s ] [ %(name)-23s ] [ %(asctime)s ] => %(message)s',
			datefmt='%d-%b-%y %H:%M:%S'
			)


		with open('hosts.yml') as yaml_:
			conf = yaml.load(yaml_, Loader=yaml.FullLoader).get('mtk_devices')
			hosts = conf['hosts']
			patterns = conf['patterns']
			var = conf['vars']


		for host in hosts.keys():

			start_time = time.time()
			logger.info("================== Logger Start @ %s ==================", ''.join(hosts[host]['mtk_host'][:]))

			MikrotikLogger = mikrotik_.MikrotikLogger(
				pattern = patterns,
				host = hosts[host]['mtk_host'],
				port = hosts[host]['mtk_port'],
				username = hosts[host]['mtk_username'],
				password = hosts[host]['mtk_password'])

			Notif = notif_.Notif(host = hosts[host]['mtk_host'])
			Notif.telegram_notif(
				token = var['telegram_token'],
				chatid = var['telegran_chatid'])

			logger.info("================== Done @ %.2f Second ==================\n\n", time.time() - start_time)

	except KeyboardInterrupt:
		sys.exit(17)
