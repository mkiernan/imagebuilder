import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

subscriptionId = os.environ.get("SUBSCRIPTION_ID", None)
credential = DefaultAzureCredential()
location = 'westus2'
resourceGroupName = "mktmpgrp"
vmssName = "redisclient"
instance_id = 0

def createComputeClient(subscriptionId, credential):
    computeClient = ComputeManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return computeClient


if __name__ == "__main__":

    computeClient = createComputeClient(subscriptionId, credential)

    vmsslist = computeClient.virtual_machine_scale_set_vms.list(resourceGroupName,vmssName)

    result = computeClient.virtual_machine_scale_set_vms.begin_delete(resourceGroupName,vmssName,instance_id)

    print("result: {}".format(result.result()))
