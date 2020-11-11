<p align="center">
  <img src="docs/logo.png">
</p>

<br/><br/>
### TLDR;
---
This python program is used to monitor, filter, and trigger log events on MikroTik RouterOS devices

the way this program works is quite simple, first this program will take logs on the MikroTik Device by making an ssh connection.

secondly, the program will filter out the word patterns that we have given / setting, for example like this `['- info', '+ ssh']`, with such a pattern, the program will get rid all logs that have the word `info` in it, either in topic and message column. and will keep logs with the word `ssh`, if the log containing the word ssh is 1 or more, the program will send a notification to the telegram bot as an alert

This program can be run anywhere, both Linux, Windows ,MacOS and agentless, meaning on the MikroTik side, no additional tools / scripts / programs are needed, **all you need is to allow ssh access to the MikroTik Device**

<br/><br/>
### USAGE
---
- first step, clone this repo, and do a few steps like the steps below to make sure this program can run perfectly
```sh
> git clone https://github.com/berrabe/python-mikrotik-logger.git
> cd python-mikrotik-logger
> pip install -r requirements.txt
```

- then, we will set some parameters that are used so that this program runs as we want, edit the **hosts.yml** file with your favorite code editor
```yaml
mtk_devices:
  patterns:
    - '- hotspot'
    - '- monitoring'
    - '+ error'
    - '+ logged'
    - '+ warning'
    - '+ down'
    - '+ rebooted'
    - '+ critical'
    - '+ failure'


  vars:
    telegram_token: < YOUR TELEGRAM TOKEN >
    telegran_chatid: '< YOUR TELEGRAM CHAT ID >'


  hosts:
    host_1:
      mtk_host: < MIKROTIK HOST IP / DOMAIN >
      mtk_port: < MIKROTIK SSH PORT >
      mtk_username: < MIKROTIK LOGIN USERNAME >
      mtk_password: < MIROTIK LOGIN PASSWORD >

```

- lastly, run this program with the command
```sh
> python3 main.py

# if you need some verbose output of what this program is doing
> cat python-mikrotik-logger.log
```

<br/><br/>
### SCREENSHOT
---
<p align="center">
  <img src="docs/terminal.png">
  <br>
</p>

<p align="center">
  <img src="docs/telegram.png">
</p>

<p align="center">
  <img src="docs/db.png">
</p>