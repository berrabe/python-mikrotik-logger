#!/bin/bash

pwd=$(pwd)

_PROC_NAME_="/usr/bin/python3 $pwd/main.py"
_COMMAND_="/usr/bin/python3 $pwd/main.py"

_CHECKING_=$(ps aux | grep -E "$_PROC_NAME_" | head -n -1 | wc -l)

if [[ $_CHECKING_ -eq 0 ]]; then
	echo " [+] No Process Found"
	echo -ne " [=] Starting Process => [ $_COMMAND_ ]\n\n"
	$_COMMAND_
else
	echo -ne " [!] $_CHECKING_ Process Found .. Aborting\n\n"
	ps aux | grep -E "$_PROC_NAME_" | head -n -1 | nl -n rn -w 3 -s ') '
	exit 1
fi
