## 基于docker的zabbix安装

* 安装mysql-server
```
docker pull mysql/mysql-server

docker run --name some-zabbix-web-apache-mysql -e DB_SERVER_HOST="172.16.103.147" -e MYSQL_USER="root" -e MYSQL_PASSWORD="123456" -e TZ="Asia/Shanghai" -e ZBX_SERVER_HOST="172.16.103.147" -d zabbix/zabbix-web-apache-mysql:latest

create database zabbix
```
* 安装zabbix-server
```
docker pull zabbix/zabbix-server-mysql

docker run --name zabbix-server -e MYSQL_USER="root" -e MYSQL_PASSWORD="123456" -e DB_SERVER_HOST="172.16.103.147" -p 10051:10051 -d zabbix/zabbix-server-mysql:latest
```
* 安装zabbix-web
```
docker pull zabbix/zabbix-web-apache-mysql

docker run --name zabbix-web -e DB_SERVER_HOST="172.16.103.147" -e MYSQL_USER="root" -e MYSQL_PASSWORD="123456" -p 7777:80 -e TZ="Asia/Shanghai" -e ZBX_SERVER_HOST="172.16.103.147" -d zabbix/zabbix-web-apache-mysql:latest
```
* 安装zabbix-agent
```
docker pull zabbix/zabbix-agent

docker run --name container_agent -e ZBX_SERVER_HOST=172.17.0.1 -e ZBX_HOSTNAME="host1" -p 10050:10050 -d zabbix/zabbix-agent:latest
```
* web ui 

```
http://172.16.103.147:7777
```
