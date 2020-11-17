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
vmssSize = 10

def createComputeClient(subscriptionId, credential):
    computeClient = ComputeManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return computeClient


if __name__ == "__main__":

    computeClient = createComputeClient(subscriptionId, credential)

    params = { "sku": {"name": "Standard_D2_v2", "capacity": vmssSize}}

    result = computeClient.virtual_machine_scale_sets.begin_update(resourceGroupName,vmssName,parameters=params)

    print("result: {}".format(result.result()))

