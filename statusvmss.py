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

def createComputeClient(subscriptionId, credential):
    computeClient = ComputeManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return computeClient


if __name__ == "__main__":

    computeClient = createComputeClient(subscriptionId, credential)

    vmsslist = computeClient.virtual_machine_scale_set_vms.list(resourceGroupName,vmssName)
    vmss_instance_view = computeClient.virtual_machine_scale_sets.get_instance_view(resourceGroupName,vmssName)

    print("vmss: {} vm_count: {} status: {}".format(vmssName,vmss_instance_view.virtual_machine.statuses_summary[0].count,
                                                  vmss_instance_view.statuses[0].display_status))

    for vm in vmsslist: 
        instance_view = computeClient.virtual_machine_scale_set_vms.get_instance_view(
                           resourceGroupName, vmssName, vm.instance_id)
        #print(instance_view) #print(instance_view.additional_properties)
        osnam = instance_view.additional_properties['osName']
        osver = instance_view.additional_properties['osVersion']
        hostname = instance_view.additional_properties['computerName']
        prov = instance_view.statuses[0].code
        power = instance_view.statuses[1].code

        print("vm name: %s hostname: %s (%s %s) instance_id: %s (%s %s)" % (vm.name,hostname,osnam,osver,vm.instance_id,prov,power))


