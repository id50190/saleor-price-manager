#!/bin/bash

set -e

# Prepare system

sudo apt update && sudo apt -y full-upgrade && sudo apt -y autoremove --purge && sudo apt autoclean

# Automatic security updates / Автоматические обновления безопасности
#
sudo apt -y install unattended-upgrades
# These lines configure unattended-upgrades so that it runs automatically. Here's what they do:
# - APT::Periodic::Update-Package-Lists "1" means that the list of packages will be automatically updated every day. / означает, что список пакетов будет автоматически обновляться каждый день.
# - APT::Periodic::Unattended-Upgrade "1"   means that the system will be updated to the latest version of the packages without the user having to intervene. / означает, что система будет обновлена до последней версии пакетов без вмешательства пользователя.
# - APT::Periodic::AutocleanInterval "7"    means that the auto-clean operation, which gets rid of old and unnecessary package files, will run once a week. / означает, что операция автоматической очистки, позволяющая избавиться от старых и ненужных файлов пакета, будет выполняться раз в неделю.
# sudo bash -c "echo 'APT::Periodic::Update-Package-Lists \"1\";' >> /etc/apt/apt.conf.d/20auto-upgrades" # set by default
# sudo bash -c "echo 'APT::Periodic::Unattended-Upgrade \"1\";'   >> /etc/apt/apt.conf.d/20auto-upgrades" # set by default
sudo bash -c "echo 'APT::Periodic::AutocleanInterval \"7\";'    >> /etc/apt/apt.conf.d/20auto-upgrades"
# Отредактировать /etc/apt/apt.conf.d/50unattended-upgrades так, чтобы система автоматически перезагружалась, когда этого требуют обновления ядра:
sudo bash -c "echo 'Unattended-Upgrade::Automatic-Reboot \"true\";' >> /etc/apt/apt.conf.d/50unattended-upgrades"
# ToDo: https://www.cyberciti.biz/faq/ubuntu-enable-setup-automatic-unattended-security-updates/
# Also: https://www.shellhacks.com/sudo-echo-to-file-permission-denied/

# sudo adduser fastapi-user # replace fastapi-user with your preferred name
# sudo gpasswd -a fastapi-user sudo # add to sudoers
# sudo groupadd web
# su - fastapi-user # login as fastapi-user 

sudo apt install software-properties-common # https://itsfoss.com/add-apt-repository-command-not-found/
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update # ?
sudo apt -y install python3.11 python3.11-venv

# Supervisor
#
sudo apt -y install supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
sudo systemctl status supervisor
sudo chown -R admin:admin /var/log/supervisor/
# supervisord # logs
# cat /var/log/supervisor/supervisord.log # logs

# Others prerequisites
#
sudo apt -y install nginx acl mc htop yarn synaptic finger curl wget lynx unzip