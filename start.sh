#!/bin/sh
/opt/bin/python /jffs/entware-ng.arm/home/AutoLogin_Mail/AutoLogin_Mail.py >> /jffs/entware-ng.arm/home/AutoLogin_Mail/log
echo '*/15 * * * * /opt/bin/python /jffs/entware-ng.arm/home/AutoLogin_Mail/AutoLogin_Mail.py >> /jffs/entware-ng.arm/home/AutoLogin_Mail/log'>>/tmp/var/spool/cron/crontabs/admin
