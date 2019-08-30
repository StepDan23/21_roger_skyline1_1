# 21_roger_skyline1_1
Web project for understanding the manual configuring application server.
# roger-skyline-1
This project, roger-skyline-1 let you install a Virtual Machine, discover the basics about system and network administration as well as a lots of services used on a server machine.

## Summary

- [Debian Installation](#VM_install)
- [Install Depedency](#depedency)
- [Configure SUDO](#sudo)
- [Setup a static IP](#static_IP)
- [Configuring up an ssh connection](#ssh_config)
- [Setup Firewall with UFW](#ufw)
- [Protection against port scans](#scan_secure)
- [Save the changes in IPtables after reboot](#save_changes)
- [Stop the services we don’t need](#stop_services)
- [Crontab Changes Monitor script](#crontab_script)
- [WEB application part](#web)
- [Deploy Part](#deploy)

<a id="VM_install"></a>
## Debian Installation 

Download [Debian Cd images](https://www.debian.org/CD/http-ftp/) and install OS on your VirtualBox.

<a id="depedency"></a>
## Install Depedency

As root:
```console
apt-get update -y && apt-get upgrade -y

apt-get install sudo vim ufw portsentry fail2ban mailutils -y
```

<a id="sudo"></a>
## Configure SUDO

Just edit the /etc/sudoers file like this

```console
vim /etc/sudoers
```

```bash
#
# This file MUST be edited with the 'visudo' command as root.
#
# Please consider adding local content in /etc/sudoers.d/ instead of
# directly modifying this file.
#
# See the man page for details on how to write a sudoers file.
#
Defaults        env_reset
Defaults        mail_badpass
Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbi$

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root    ALL=(ALL:ALL) ALL
USER_NAME     ALL=(ALL:ALL) NOPASSWD:ALL

# Members of the admin group may gain root privileges

# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d
```

<a id="static_IP"></a>
## Setup a static IP

In virtualbox's setings you have to add new virtual network (Go to File -> Host Network Manager(cmd+w) -> Add new one).
A network will named vboxnet0. Check DHCP server checkbox (disabled).

In the settings of our virtual machine you have to add new network adapter (Host-only network), check cable connection checkbox (enable) in advance setings.

1. Edit the file `/etc/network/interfaces` and setup connection for Internet access (enp0s3) and for static ip connection (enp0s8)

```console
sudo vim /etc/network/interfaces
```

```bash
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

#loopback
auto lo
iface lo inet loopback

#primary inet
auto enp0s3
iface enp0s3 inet dhcp

#static web
auto enp0s8
iface enp0s8 inet static
	address 192.168.56.2
	netmask 255.255.255.252
```

2. Restart the network service to make changes effective

```console
sudo service networking reload
sudo service networking restart
```

3. Check the result with the following command

```console
ip a
```

<a id="ssh_config"></a>
## Configuring up an ssh connection

1.  Edit the line 13 in /etc/ssh/sshd_config which states 'Port 22'

```console
sudo vim /etc/ssh/sshd_config
```

> **Note**: The Internet Assigned Numbers Authority (IANA) is responsible for the global coordination of the DNS Root, IP addressing, and other Internet protocol resources. It is good practice to follow their port assignment guidelines. Having said that, port numbers are divided into three ranges: Well Known Ports, Registered Ports, and Dynamic and/or Private Ports. The Well Known Ports are those from 0 through 1023 and SHOULD NOT be used. Registered Ports are those from 1024 through 49151 should also be avoided too. Dynamic and/or Private Ports are those from 49152 through 65535 and can be used. Though nothing is stopping you from using reserved port numbers, our suggestion may help avoid technical issues with port allocation in the future.

2. Generate a public/private rsa key pair

```console
ssh-keygen -t rsa
```

This command will generate 2 files `id_rsa` and `id_rsa.pub`

- **id_rsa**:  Our private key, should be keep safely, She can be crypted with a password.
- **id_rsa.pub** Our private key, you have to transfer this one to the server.

3. To do that we can use the `ssh-copy-id` command

```console
ssh-copy-id -i id_rsa.pub USER_NAME@192.168.56.2 -p 50023
```

The key is automatically added in `~/.ssh/authorized_keys` on the server

4. Edit `/etc/ssh/sshd.config` file to remove root login permit, password authentification 

```console
sudo vim /etc/ssh/sshd.conf
```

- Edit line 32 like: `PermitRootLogin no`
- Edit line 56 like `PasswordAuthentication no`

5. Restart the SSH daemon service

```console
sudo service ssh reload
sudo service ssh restart
sudo service sshd restart
```

6. Connect to your VM using ssh-key authentication

```console
USER_NAME@192.168.56.2 -p 50023
```

<a id="ufw"></a>
## Setup Firewall with UFW

1. Make sure ufw is enable
 
 ```console
 sudo ufw enable
 sudo ufw status
 ```
 
2. Setup firewall rules
      - SSH : `sudo ufw allow 50683/tcp`
      - HTTP : `sudo ufw allow 80/tcp`
      - HTTPS : `sudo ufw allow 443`

3. Setup Denial Of Service Attack with fail2ban
      
```console
sudo vim /etc/fail2ban/jail.conf
```

```bash
[sshd]
port = 50023
enabled = true
maxretry = 5
findtime = 120
bantime = 60

#Dos HTTP/HTTPS:
[http-get-dos]
enabled = true
port = http,https
filter = http-get-dos
logpath = /var/log/apache2/access.log
maxretry = 300
findtime = 300
bantime = 60
action = iptables[name=HTTP, port=http, protocol=tcp]
```

4. Add http-get-dos filter

```console
sudo vim /etc/fail2ban/filter.d/http-get-dos.conf
```

```bash
[Definition]
failregex = ^<HOST> -.*"(GET|POST).*
ignoreregex =
```

5. Reload our firewall and fail2ban

```console
sudo ufw reload
sudo service fail2ban restart
```

<a id="scan_secure"></a>
## Protection against port scans

1. Config portsentry

```console
sudo vim /etc/default/portsentry
```

```bash
TCP_MODE="atcp"
UDP_MODE="audp"
```

2. Edit the configurationg file

```console
sudo vim /etc/portsentry/portsentry.conf
```

```bash
BLOCK_UDP="1"
BLOCK_TCP="1"
```

- Comment the current `KILL_ROUTE` and uncomment the following one

```bash
KILL_ROUTE="/sbin/iptables -I INPUT -s $TARGET$ -j DROP"
```

- Comment the following line

```bash
KILL_HOSTS_DENY="ALL: $TARGET$ : DENY
```

3. Restart the service to make changes effectives

```console
sudo service portsentry restart
```

<a id="save_changes"></a>
## Save the changes in IPtables after reboot

1. Make settings dump and save in in /etc/iptables/ folder

```console
sudo iptables-save > /etc/iptables/rules.v1
```

2. Write a script to load the settings dump in /etc/network/if-pre-up.d/iptables

```console
sudo vim /etc/network/if-pre-up.d/iptables
```

```bash
#!/bin/bash
sudo iptables-restore < /etc/iptables/rules.v1
exit 0
```

3. Make the script executable

```console
sudo chmod+x /etc/network/if-pre-up.d/iptables
```

<a id="stop_services"></a>
## Stop the services we don’t need 

```console
sudo systemctl disable <services inutiles>
```

Check the list of all services status on your vm:

```console
sudo systemctl list-unit-files
```

<a id="update_script"></a>
## Update Packages srcipt

1. Create the `update_and_log.sh` script

```console
sudo vim update_and_log.sh
```

```bash
#! /bin/bash
sudo apt-get update -y && sudo apt-get upgrade -y >> /var/log/update_script.log
```

2. Change the crontab file for make weekly task

```console
sudo vim /etc/crontab
```

```bash
0 4	* * 1	root	sh /home/USER_NAME/update_and_log.sh
@reboot		root	sh /home/USER_NAME/update_and_log.sh
```

<a id="crontab_script"></a>
## Crontab Changes Monitor script

1. Create the `crontab_monitor_changes.sh` script

```console
sudo vim crontab_monitor_changes.sh
```

```bash
#! /bin/bash
DIFF=$(diff -U 3 /home/ste/crontab_tmp /etc/crontab)
if [ "$DIFF" != "" ];
	then
	echo "$DIFF" | mail -s "/etc/crontab file has been modified." root
	cp /etc/crontab /home/ste/crontab_tmp
fi
```

2. Change the crontab file for make daily task

```console
sudo vim /etc/crontab
```

```bash
0 0	* * *	root	sh /home/ste/crontab_monitor_changes.sh
```

<a id="web"></a>
## WEB application part

1. Write web application on python Flask like one of this
[Login web page with Flask](https://pythonspot.com/login-authentication-with-flask/)

2. Install Nginx on your VM
[Nginx Installation](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-debian-9)

3. Configure Nginx with uWSGI
[Configurating Nginx tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04)

4. Create a Self-Signed SSL Certificate for Nginx
[Creating SSL for Nginx tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-on-debian-9) 

<a id="deploy"></a>
## Deploy Part

Write a script for automatic deployment of new changes on your web application like this one

```bash
#! /bin/bash
FOLDER=/home/ste/git_repo
GIT_URL=https://github.com/StepDan23/21_roger_skyline_1.git

git clone $GIT_URL $FOLDER
cp -r $FOLDER/webpage/ .
rm -rdf $FOLDER
sudo service webpage restart
sudo service nginx restart
```
