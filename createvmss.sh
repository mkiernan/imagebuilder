#!/bin/bash -x

# create the redis vm from the image builder or packer image

# import global variables
source header.sh

# create infra
# virtual network 
az network vnet create \
 --resource-group $gridResourceGroup \
 --name gridvnet \
 --address-prefix 10.0.0.0/16 \
 --subnet-name compute \
 --subnet-prefix 10.0.0.0/22

# proximity placement group
az ppg create \
  --name gridppg \
  --resource-group $gridResourceGroup \
  --location $location

# create a vm from the image
az vm create \
  --resource-group $gridResourceGroup \
  --name redisserver \
  --size Standard_F2S_v2 \
  --admin-username gridadmin \
  --location $location \
  --image $REDISSERVERIMAGE \
  --ppg gridppg \
  --vnet-name gridvnet \
  --subnet compute \
  --generate-ssh-keys

#-- open the redis port
az vm open-port --port 6379 --name redisserver --resource-group $gridResourceGroup

# harvest the public ip address
ip=$(az vm show --name redisserver -g $gridResourceGroup --show-details --query publicIps | tr -d '"')
echo "VM is ready: ssh gridadmin@$ip"

# create a vm from the client image
az vmss create \
  --resource-group $gridResourceGroup \
  --vm-sku Standard_F2S_v2 \
  --name gridvmss \
  --admin-username gridadmin \
  --location $location \
  --image $REDISCLIENTIMAGE \
  --instance-count 2 \
  --vnet-name gridvnet \
  --subnet compute \
  --ppg gridppg \
  #--custom-data cloud-init.txt \
  --generate-ssh-keys

# harvest the public ip address
echo "VMSS is ready: ssh IPADDRESS PORT -lgridadmin"
az vmss list-instance-connection-info --name gridvmss -g $gridResourceGroup
