# Traduze frontend
Django based frontend


### Installation

```
cd /opt/traduze_frontend
virtualenv venv -p python3.6
source venv/bin/activate

sudo apt-get install libmysqlclient-dev
sudo apt-get install python3-dev
sudo apt-get install gettext



pip install -r requirements.txt
python manage.py compilemessages

sudo dpkg -i tidy-5.4.0-64bit.deb
```

Create database

```
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 's3cretPassword';
FLUSH PRIVILEGES;
CREATE DATABASE traduze;
exit;
```

```
python manage.py makemigrations app
python manage.py migrate

python manage.py collectstatic
python manage.py createsuperuser

(optional)
python manage.py runserver 0.0.0.0:9124
```


### Apache
```
cp apache_configs/traduze.conf /etc/apache2/sites-available/
a2ensite traduze.conf
cd /opt/traduze_frontend
mkdir log
sudo apt-get install libapache2-mod-wsgi-py3
sudo service apache2 restart
```
