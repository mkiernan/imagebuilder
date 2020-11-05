#!/bin/bash
#
# Install Redis on RHEL 8.2
#
set -xeo pipefail #-- strict/exit on fail
exec 2>&1 # funnel stderr back to packer client console

usage()
{
   echo -e "\nUsage: $(basename $0) [client][server]"
   exit 1
}

if [[ $(id -u) -ne 0 ]] ; then
        echo "Must be run as root"
        exit 1
fi

if [ $# -ne 1 ]; then
   usage
fi

clsvr=$1

#- needed for startup.py unless performaed in cloudinit
yum install -y gcc python3-devel
pip3 install psutil

dnf module install redis -y
#echo "vm.overcommit_memory=1" > /etc/sysctl.conf
#echo never > /sys/kernel/mm/transparent_hugepage/enabled
sed -i "s/^bind 127\.0\.0\.1/bind 0\.0\.0\.0/g" /etc/redis.conf
firewall-cmd --add-port=6379/tcp --permanent
firewall-cmd --reload
#-- enable only if server
if [ $clsvr = "server" ]; then
   systemctl enable redis
fi
#systemctl start redis
#systemctl status redis
echo done
