#! /bin/bash
DIFF=$(diff -U 3 /home/ste/crontab_tmp /etc/crontab)
if [ "$DIFF" != "" ];
	then
	echo "$DIFF" | mail -s "/etc/crontab file has been modified." root
	cp /etc/crontab /home/ste/crontab_tmp
fi
