# Deploying Airbyte on a Non-Standard Operating System

## CentOS 8

From clean install:

```
firewall-cmd --zone=public --add-port=8000/tcp --permanent
firewall-cmd --zone=public --add-port=8001/tcp --permanent
firewall-cmd --zone=public --add-port=7233/tcp --permanent
systemctl restart firewalld
```
OR... if you prefer iptables:
```
iptables -A INPUT -p tcp -m tcp --dport 8000 -j ACCEPT
iptables -A INPUT -p tcp -m tcp --dport 8001 -j ACCEPT
iptables -A INPUT -p tcp -m tcp --dport 7233 -j ACCEPT
systemctl restart iptables
```
Setup the docker repo:
```
dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo`
dnf install docker-ce --nobest
systemctl enable --now docker
usermod -aG docker $USER
```
You'll need to get docker-compose separately.
```
dnf install wget git curl
curl -L https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
Now we can install Airbyte. In this example, we will install it under `/opt/`
```
cd /opt
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
docker-compose ps
```