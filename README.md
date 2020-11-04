# Azure Image Builder & Packer examples for Grid Computing

This repo provides example code for automating deployment of a simple grid with RHEL 8.2 + Redis using custom images. 

Three image creation methods are provided. The recommended options are packer or imagebuilder: 

1. packer -> build with <a href="https://www.packer.io/">packer</a>
2. imagebuilder -> build with <a href="https://docs.microsoft.com/en-us/azure/virtual-machines/linux/image-builder-overview">Azure ImageBuilder</a>
3. manual -> build image with a manual <a href="https://docs.microsoft.com/en-us/azure/virtual-machines/linux/tutorial-custom-images">procedure</a>.

Azure cli scripts & python code is also provided to deploy the images as simple redis server vm + client vmss

Clone the repo with: https://github.com/mkiernan/imagebuilder.git.

# Part 1: Prepare your environment 

a. Install <a href="https://docs.microsoft.com/en-us/cli/azure/install-azure-cli">azure cli</a>, or utilize <a href="https://shell.azure.com">shell.azure.com</a> 

b. Create service principal 

Follow instructions <a href="https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli">here</a>. 

c. Set environment variables

Take the output from a. and create environment variables with your service principle + secret

export SUBSCRIPTION_ID="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
export AZURE_TENANT_ID="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
export AZURE_CLIENT_ID="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
export AZURE_CLIENT_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Part 2: Build the Image

## Packer Image Build Instructions

Download the packer executable and build the images: 

```
cd packer;./getpacker.sh; ./dopacker.sh
```

## ImageBuilder Instructions

Imagebuilder embeds packer in the service; build the images as follows: 

```
cd imagebuilder
./buildimage.sh
```

## Manual Image Build Instructions

Build the image by hand by adapting the example provided: 

```
./buildimage_trad.sh
```

# Part 3: Deploy the images 

## Build the infrastructure

Wait for the images to be created, and then deploy with either the azure cli script: 
```
./createvmss.sh
```
or the python script (they both do the same thing): 
```
python3 createvmss.py
``
