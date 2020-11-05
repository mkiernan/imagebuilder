#!/bin/bash -xe

# import global variables
source header.sh

# resource group
az group create -n $imageResourceGroup -l $location

# create golden image
# To get the latest list run:
#  az vm image list --location westus2 --publisher RedHat --sku 8.1 --all -o table
imageUrn="RedHat:RHEL:8.1:8.1.2020082711"
az vm create \
 --name Golden01 \
 --resource-group $imageResourceGroup \
 --location $location \
 --image  $imageUrn \
 --size Standard_DS2_v2 \
 --admin-username azureuser \
 --generate-ssh-keys

 # harvest the public ip address
ip=$(az vm show --name Golden01 -g iblinuxgalleryrg --show-details --query publicIps | tr -d '"')
echo "VM is ready: ssh azureuser@$ip"

echo "Login and customize your VM, then run the following manual steps:"
echo "sudo waagent -deprovision+user"
echo "logout"
echo "az vm deallocate --resource-group $imageResourceGroup --name Golden01"
echo "az vm generalize --resource-group $imageResourceGroup --name Golden01"
echo "az image create --resource-group $imageResourceGroup --name GoldenImage --source Golden01"
echo "List images:"
echo "az image list -o table"
echo "Then finally create a new VM or VMSS from the image:"
echo "az vm create --resource-group $imageResourceGroup --name TestVM --image GoldenImage --admin-user azureuser --generate-ssh-keys"
