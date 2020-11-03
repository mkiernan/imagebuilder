#!/bin/bash -x
#PACKER_LOG=1 ./packer build -debug -force redis_rhel.json
./packer  build -force redisclient_rhel.json
./packer  build -force redisserver_rhel.json
