#!/bin/bash -x

packer_version=1.6.4
packerzip=https://releases.hashicorp.com/packer/$packer_version/packer_${packer_version}_linux_amd64.zip
wget $packerzip -O packer.zip && unzip packer.zip && rm -f packer.zip 
