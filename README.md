Linux Server Configuration
Linux - Apache - Flask - Postgresql



Update system with latest packages
===========================================================
apt-get update
apt-get upgrade

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
    - "chmod 600 .ssh/authorized_keys"

