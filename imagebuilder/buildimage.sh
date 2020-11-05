#!/bin/bash -xe

# import global variables
source header.sh

# resource group
az group create -n $imageResourceGroup -l $location

# create user assigned identity for image builder to access the storage account where the script is located
az identity create -g $imageResourceGroup -n $identityName

# get identity id
imgBuilderCliId=$(az identity show -g $imageResourceGroup -n $identityName | grep "clientId" | cut -c16- | tr -d '",')

# this command will download an Azure role definition template, and update the template with the parameters specified earlier.
curl https://raw.githubusercontent.com/danielsollondon/azvmimagebuilder/master/solutions/12_Creating_AIB_Security_Roles/aibRoleImageCreation.json -o aibRoleImageCreation.json

# update the definition
sed -i -e "s/<subscriptionID>/$subscriptionID/g" aibRoleImageCreation.json
sed -i -e "s/<rgName>/$imageResourceGroup/g" aibRoleImageCreation.json
sed -i -e "s/Azure Image Builder Service Image Creation Role/$imageRoleDefName/g" aibRoleImageCreation.json

# create role definitions
az role definition create --role-definition ./aibRoleImageCreation.json
echo "Role definition Created"
#-- can take up to 3 minutes 
rt="[]"
while [[ "$rt" == "[]" ]]; do
   rt=$(az role definition list -g $imageResourceGroup --name $imageRoleDefName)
   sleep 30
done

# grant role definition to the user assigned identity
az role assignment create \
    --assignee $imgBuilderCliId \
    --role $imageRoleDefName \
    --scope /subscriptions/$subscriptionID/resourceGroups/$imageResourceGroup

echo "Roll Assignment Created"
sleep 30

# create shared image gallery
az sig create -g $imageResourceGroup --gallery-name $sigName

sleep 30

#  create the image definition
#--sku 18.04-LTS \
az sig image-definition create \
   -g $imageResourceGroup \
   --gallery-name $sigName \
   --gallery-image-definition $imageDefName \
   --publisher myIbPublisher \
   --offer myOffer \
   --sku 8.1 \
   --os-type Linux

sleep 30

# get the json template for building the image - use a PAT (Personal Access Token) since this is a private repo
#curl https://raw.githubusercontent.com/danielsollondon/azvmimagebuilder/master/quickquickstarts/1_Creating_a_Custom_Linux_Shared_Image_Gallery_Image/helloImageTemplateforSIG.json -o helloImageTemplateforSIG.json
curl -H 'Authorization: token e83708801b2c1bb60fe405bbde80029ccb305028' -H 'Accept:application/vnd.github.VERSION.raw' https://raw.githubusercontent.com/mkiernan/BankofAmerica/master/RHELImageTemplateSIG.json -o RHELImageTemplateSIG.json
sed -i -e "s/<subscriptionID>/$subscriptionID/g" RHELImageTemplateSIG.json
sed -i -e "s/<rgName>/$imageResourceGroup/g" RHELImageTemplateSIG.json
sed -i -e "s/<imageDefName>/$imageDefName/g" RHELImageTemplateSIG.json
sed -i -e "s/<sharedImageGalName>/$sigName/g" RHELImageTemplateSIG.json
sed -i -e "s/<region1>/$location/g" RHELImageTemplateSIG.json
sed -i -e "s/<region2>/$additionalregion/g" RHELImageTemplateSIG.json
sed -i -e "s/<runOutputName>/$runOutputName/g" RHELImageTemplateSIG.json
sed -i -e "s%<imgBuilderId>%$imgBuilderId%g" RHELImageTemplateSIG.json

# submit the template to the builder
az resource create \
    --resource-group $imageResourceGroup \
    --properties @RHELImageTemplateSIG.json \
    --is-full-object \
    --resource-type Microsoft.VirtualMachineImages/imageTemplates \
    -nRHELImageTemplateSIG

sleep 30

# cause the image to get built
az resource invoke-action \
     --resource-group $imageResourceGroup \
     --resource-type  Microsoft.VirtualMachineImages/imageTemplates \
     -n RHELImageTemplateSIG\
     --action Run

echo ""
echo " *** Image build complete *** "