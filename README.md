Linux Server Configuration
Linux - Apache - Flask - Postgresql

Server information
===========================================================
IP: 52.33.66.244
SSH port: 2200
App URL: http://ec2-52-33-66-244.us-west-2.compute.amazonaws.com/catalog/

Update system with latest packages
===========================================================
- "apt-get update"
- "apt-get upgrade"

SSH port change
===========================================================
Change port in sshd_config
  - "nano /etc/ssh/sshd_Config"
  - Change "Port 22" to "Port 2200"
  - Restart SSH
    - "service ssh restart"

Firewall configuration
  - Block all incoming except port 2200, 80 (www) and NTP, and enable firewall
===========================================================
- "ufw default deny incoming"
- "ufw default allow outgoing"
- "ufw allow 2200/tcp""
- "ufw allow www"
- "ufw allow ntp"
- "ufw enable"

Change server timezone to UTC
===========================================================
Run package configuration script for tzdata
  - "dpkg-reconfigure tzdata"
  - Choose "None of the above"
  - Choose "UTC"

Apache installation/configuration
===========================================================
Install Apache
  - "apt-get install apache2"

Install wsgi support
  - "apt-get install libapache2-mod-wsgi-py3"

Disable default site
  - "a2dissite 000-default"

Postgresql installation/configuration
===========================================================
Install Postgresql
  - "apt-get install postgresql postgresql-contrib"

Update config file
  - "nano /etc/postgresql/9.3/main/postgresql.conf"
    - Set "listen_addresses" to "localhost"
  - Restart postgresql
    - "service postgresql restart"

Add "catalog" user to postgresql
  - "postgres createuser catalog"
  - Set password
    - "postgres psql"
    - "\password catalog"
    - Enter password

Git installation
===========================================================
Install Git
  - "apt-get install git"

Catalog application setup
===========================================================
Install python modules
  - "apt-get install python-pip"
  - "pip install flask"
  - "pip install sqlalchemy"
  - "pip install oauth2client"

Install site from GIT
  - "mkdir /var/www/catalog"
  - "cd /var/www/catalog"
  - "git clone https://github.com/jbrunette/catalog"

Create Apache application site
  - "nano /etc/apache2/sites-enabled/catalog.conf"
  - Enable site
    - "a2ensite catalog"

Restart Apache
  - "service apache2 restart"

"grader" user setup
===========================================================
Add user "grader" to system
  - "adduser grader"

Give grader "sudo" ability
  - "nano /etc/sudoers.d/grader"
  - Set file contents to:
    grader ALL=(ALL) NOPASSWD:ALL
  - Set file permissions on grader file
    - "chmod 0440 /etc/sudoers.d/grader"

Set up SSH access for grader
  - "mkdir /home/grader/.ssh"
  - "nano /home/grader/.ssh/authorized_keys"
  - Add SSH private key to file
  - Change permissions
    - "chmod 700 /home/grader/.ssh"
    - "chmod 600 /home/grader/.ssh/authorized_keys"

