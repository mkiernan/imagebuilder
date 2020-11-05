#!/bin/bash -x

# Resource group name
imageResourceGroup=mkimagegrp
gridResourceGroup=mktmpgrp

# Datacenter location - we are using West US 2 in this example
location=westus2

# Additional region to replicate the image to - we are using East US in this example
additionalregion=eastus

# IMAGEBUILDER or PACKER IMAGE string here:
#IMAGE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$imageResourceGroup/providers/Microsoft.Compute/galleries/$sigName/images/$imageDefName/versions/latest"
# Packer image strings: 
REDISSERVERIMAGE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$imageResourceGroup/providers/Microsoft.Compute/images/redisserverImage"
REDISCLIENTIMAGE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$imageResourceGroup/providers/Microsoft.Compute/images/redisclientImage"

# name of the shared image gallery - in this example we are using myGallery
sigName=GridIbGallery

# name of the image definition to be created - in this example we are using myImageDef
imageDefName=GridIbImageDef

# image distribution metadata reference name
runOutputName=aibLinuxSIG

# create user assigned identity for image builder to access the storage account where the script is located
#identityName=aibBuiUserId$(date +'%s')
identityName=aibBuiUserMK

# get the user identity URI, needed for the template
imgBuilderId=/subscriptions/$SUBSCRIPTION_ID/resourcegroups/$imageResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$identityName

# create image definition name
#imageRoleDefName="AzureImageBuilderImageDef"$(date +'%s')
imageRoleDefName="AzureImageBuilderImageDef"
