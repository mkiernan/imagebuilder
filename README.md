# Azure Image Builder & Packer examples for Grid Computing

Three deployment options are provided: 

1. packer -> build with packer
2. imagebuilder -> build with Azure ImageBuilder
3. manual -> build image manually

Other azure cli scripts & python code provided to deploy a simple redis server vm + client vmss

Clone the repo first with: https://github.com/mkiernan/imagebuilder.git

## Packer Instructions

```
cd packer
./getpacker.sh
./dopacker.sh
```
Wait for the images to be created, and then deploy with:
```
./createvmss
```

## ImageBuilder Instructions

```
cd imagebuilder
./buildimage.sh
```
