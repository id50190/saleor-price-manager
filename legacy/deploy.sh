#!/bin/bash

set -e

APP_NAME="fastapi-app"
APP_PATH="/srv/$APP_NAME"

# Prepare system
#
./deploy.pt1.sh

# Deploy application
#
sudo mkdir -p $APP_PATH && sudo chown -R $USER:$USER "$APP_PATH"
cd $APP_PATH && git clone https://github.com/PSYCHONOISE/fastapi-app-template.git .
rm -rf .git && git init
if [ -d "env" ]; then rm -rf ./env; fi
chmod 750 .                          # drwxr-x---
find . -type f -exec chmod 640 {} \; # frw-r-----
find . -type d -exec chmod 750 {} \; # drwxr-x---
chmod u+x ./deploy.sh
chmod u+x ./save.sh
python3 -m venv env && . env/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.lock.txt && deactivate
# sudo ufw allow 8080
# uvicorn main:app --host 0.0.0.0 --port 8080 # Verify that everything went well by running the application, e.g. use `curl localhost:8080`

# Configuring Supervisor
#
echo '#!/bin/bash' > ./bang.sh
sudo bash -c "cat <<\EOF >> ./bang.sh
#\!/bin/bash

set -e

# . .env && . env/bin/activate && uvicorn main:app --reload --host $APPLICATION_HOST --port $APPLICATION_PORT

NAME=$APP_NAME
DIR=$APP_PATH
USER=$USER
GROUP=$USER
WORKERS=3
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=\"\$DIR/env/bin/activate\"
BIND=unix:\"\$DIR/run/gunicorn.sock\"
LOG_LEVEL=error

cd \"\$DIR\"
source \"\$VENV\"

exec gunicorn main:app \\
  --name \"\$NAME\" \\
  --workers \"\$WORKERS\" \\
  --worker-class \"\$WORKER_CLASS\" \\
  --user=\"\$USER\" \\
  --group=\"\$GROUP\" \\
  --bind=\"\$BIND\" \\
  --log-level=\"\$LOG_LEVEL\" \\
  --log-file=-
EOF"
chmod u+x ./bang.sh
sudo bash -c "cat <<\EOF > /etc/supervisor/conf.d/fastapi-app.conf
[program:$APP_NAME]
command=$APP_PATH/bang.sh
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_PATH/log/gunicorn-error.log
EOF"
sudo supervisorctl reread
sudo supervisorctl update
# sudo supervisorctl reload
sudo supervisorctl status fastapi-app
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" --unix-socket "$APP_PATH/run/gunicorn.sock" localhost) # Отправляем запрос с помощью curl и сохраняем код ответа
if [ "$HTTP_CODE" -eq 200 ]; # Проверяем код ответа
then echo "Successful request. Response code: $HTTP_CODE"
elif [ "$HTTP_CODE" -eq 404 ]; then echo "Error 404: Page not found.";        exit 0
elif [ "$HTTP_CODE" -eq 500 ]; then echo "Error 500: Internal server error."; exit 0
else                                echo "Unknown response code: $HTTP_CODE"; exit 0; fi
#
# TechDebt: https://stackoverflow.com/questions/19737511/gunicorn-throws-oserror-errno-1-when-starting
#
# PS. if you make changes to the code, you can restart the service to apply to changes by running this command: `sudo supervisorctl restart fastapi-app`

# Configuring Nginx
#
# sudo usermod -aG $USER www-data # groups www-data
sudo setfacl -m u:www-data:rx $(echo "$APP_PATH/run" | awk -F/ 'BEGIN{OFS="/"} {for (i=2; i<=NF; i++) {path=path"/"$i; print path}}') # Make sure you are using the www-data user that Nginx runs on behalf of by `ps aux | grep nginx` 
# sudo getfacl $(echo "$APP_PATH/run" | awk -F/ 'BEGIN{OFS="/"} {for (i=2; i<=NF; i++) {path=path"/"$i; print path}}') # Check.
sudo bash -c "cat <<\EOF > /etc/nginx/sites-available/$APP_NAME
upstream app_server {
  server unix:$APP_PATH/run/gunicorn.sock fail_timeout=0;
}

server {
  listen 8080;
  server_name _; # Add here the ip address of your server or a domain pointing to that ip (like example.com or www.example.com).

  keepalive_timeout 5;
  client_max_body_size 4G;

  access_log $APP_PATH/log/nginx-access.log;
  error_log  $APP_PATH/log/nginx-error.log;

  location / {
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header Host \$http_host;
    proxy_redirect off;

EOF" && sudo bash -c "echo '    if (!-f \$request_filename) {' >> /etc/nginx/sites-available/$APP_NAME" && sudo bash -c "cat <<\EOF >> /etc/nginx/sites-available/$APP_NAME
      proxy_pass http://app_server;
      break;
    }
  }
}
EOF"
sudo ln -s "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/$APP_NAME"
sudo nginx -t && sudo nginx -s reload && sudo systemctl status nginx
# Optionally, set up password authentication with Nginx
# sudo sh -c "echo -n 'grasper:' >> /etc/nginx/.htpasswd" #  Create a hidden file to store our username and password combinations.
# sudo sh -c "openssl passwd -apr1 >> /etc/nginx/.htpasswd" # Add an encrypted password entry for the username (by hands)
# cat /etc/nginx/.htpasswd # Optionally, you can see how the usernames and encrypted passwords are stored
# Also, you can create the password file using Apache Utilities: https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-14-04, https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/

# sudo apt install snapd
# sudo snap install core; sudo snap refresh core
# sudo snap install --classic certbot
# sudo ln -s /snap/bin/certbot /usr/bin/certbot

# https://app.zerossl.com/certificate/new