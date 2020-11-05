#!/bin/bash -x

# import global variables
source header.sh

# get identity id
imgBuilderCliId=$(az identity show -g $imageResourceGroup -n $identityName | grep "clientId" | cut -c16- | tr -d '",')

# delete image builder template
az resource delete \
    --resource-group $imageResourceGroup \
    --resource-type Microsoft.VirtualMachineImages/imageTemplates \
    -n RHELImageTemplateSIG

# delete permissions assignments, roles and identity
az role assignment delete \
    --assignee $imgBuilderCliId \
    --role "$imageRoleDefName" \
    --scope /subscriptions/$subscriptionID/resourceGroups/$imageResourceGroup

az role definition delete --name "$imageRoleDefName"

az identity delete --ids $imgBuilderId

# Get the image version created by image builder, this always starts with 0.,
# and then delete the image version
sigDefImgVersion=$(az sig image-version list \
   -g $imageResourceGroup \
   --gallery-name $sigName \
   --gallery-image-definition $imageDefName \
   --subscription $subscriptionID --query [].'name' -o json | grep 0. | tr -d '"'| head -1 | tr -d ',' )

az sig image-version delete \
   -g $imageResourceGroup \
   --gallery-image-version $sigDefImgVersion \
   --gallery-name $sigName \
   --gallery-image-definition $imageDefName \
   --subscription $subscriptionID

# delete the image definition
az sig image-definition delete \
   -g $imageResourceGroup \
   --gallery-name $sigName \
   --gallery-image-definition $imageDefName \
   --subscription $subscriptionID

# delete the gallery
az sig delete -r $sigName -g $imageResourceGroup

# delete the vm
az vm delete --name redisservervm --resource-group $imageResourceGroup -y
az vm delete --name Golden01 --resource-group $imageResourceGroup -y
az vm delete --name TestVM --resource-group $imageResourceGroup -y

# delete the vmss
az vmss delete --name gridvmss  --resource-group $imageResourceGroup

# delete the ppg
az ppg delete --name gridppg --resource-group $imageResourceGroup

# delete the vnet
az network vnet delete --name gridvnet --resource-group $imageResourceGroup

# delete the resources group
az group delete -n $imageResourceGroup -y
