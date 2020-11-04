#!/bin/bash -e

# edit environment keys into config and run packer

maskfile()
{
   INPUT=$1
   OUTPUT="/tmp/packer.$INPUT.$$"
   cp -p $INPUT $OUTPUT; chmod 600 $OUTPUT
   sed -i -e "s/\"client_id\": \"<REPLACE>\"/\"client_id\": \"$AZURE_CLIENT_ID\"/g" $OUTPUT
   sed -i -e "s/\"client_secret\": \"<REPLACE>\"/\"client_secret\": \"$AZURE_CLIENT_SECRET\"/g" $OUTPUT
   sed -i -e "s/\"tenant_id\": \"<REPLACE>\"/\"tenant_id\": \"$AZURE_TENANT_ID\"/g" $OUTPUT
   sed -i -e "s/\"subscription_id\": \"<REPLACE>\"/\"subscription_id\": \"$SUBSCRIPTION_ID\"/g" $OUTPUT
   echo "$OUTPUT"
}

#PACKER_LOG=1 ./packer build -debug -force redis_rhel.json

packerconfig1=$(maskfile "redisclient_rhel.json") 
packerconfig2=$(maskfile "redisserver_rhel.json")

trap "rm -f $packerconfig1 $packerconfig2" SIGINT EXIT

./packer  build -force $packerconfig1
./packer  build -force $packerconfig2

rm -f $packerconfig1 $packerconfig2
