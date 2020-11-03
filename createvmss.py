# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import random
import string
import logging

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

logger = logging.getLogger()
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def createResourceClient(subscriptionId, credential):
    resourceClient = ResourceManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return resourceClient


def createNetworkClient(subscriptionId, credential):
    networkClient = NetworkManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return networkClient


def createComputeClient(subscriptionId, credential):
    computeClient = ComputeManagementClient(
        credential=credential, subscription_id=subscriptionId)
    return computeClient


def main():
    # Assumes that these environment variables are set SUBSCRIPTION_ID, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

    subscriptionId = os.environ.get("SUBSCRIPTION_ID", None)
    credential = DefaultAzureCredential()
    location = 'westus2'
    resourceGroupName = "mktmpgrp"
    imageResourceGroupName = "mkimagegrp"
    subnetName = "compute"
    interfaceName = "interfaceName"
    networkName = "gridvnet"
    adminUserName = "adminUserName"
    adminPassword = "Azur3Passw0rd"

    serverimageName = "redisserverImage"
    clientimageName = "redisclientImage"
    vmName = "redisserver"
    vmssName = "redisclient"
    vmssInstances = 2
    loadbalancerName = "vmssloadbalancer"
    loadbalancerFrontEndIpConfName = "loadBalancerFrontEnd"

    resourceClient = createResourceClient(subscriptionId, credential)

    resourceDict = {'location': 'westus2'}
    resourceClient.resource_groups.create_or_update(
        resourceGroupName, resourceDict)

    networkClient = createNetworkClient(subscriptionId, credential)

    vnetDict = {'location': 'westus2', 'address_space': {
        'address_prefixes': ['10.0.0.0/16']}}
    vnet = networkClient.virtual_networks.begin_create_or_update(
        resourceGroupName, networkName, vnetDict).result()

    subnetDict = {'address_prefix': '10.0.0.0/22'}
    subnet = networkClient.subnets.begin_create_or_update(
        resourceGroupName, networkName, subnetName, subnetDict).result()

    publicIpDict = {"location": 'westus2', "public_ip_allocation_method": "Static",
                    "public_ip_address_version": "IPV4", "sku": {"name": "Standard"}}
    publicIp = networkClient.public_ip_addresses.begin_create_or_update(
        resourceGroupName, "public_ip_address_name", publicIpDict).result()

    nicDict = {'location': 'westus2', 'ip_configurations': [
        {'name': 'ipconfig', 'subnet': {'id': subnet.id}, "public_ip_address": {"id": publicIp.id}}]}
    nic = networkClient.network_interfaces.begin_create_or_update(
        resourceGroupName, interfaceName, nicDict).result()
    logger.debug("NIC:%s" % dir(nic))

    # -- create load balancer for vmss
    lbpublicIpDict = {"location": "westus2", "public_ip_allocation_method": "Static",
                      "public_ip_address_version": "IPV4", "sku": {"name": "Standard"}}

    lbpublicIp = networkClient.public_ip_addresses.begin_create_or_update(
        resourceGroupName, "lb_public_ip_address_name", lbpublicIpDict).result()

    logger.debug("LB PublicIP: %s " % lbpublicIp.id)

    frontendIpConf = {"name": loadbalancerFrontEndIpConfName ,
                     "public_ip_address": {
                          "id": lbpublicIp.id
                          },
                     "private_ip_allocation_method": "Dynamic",
                     "private_ip_address_version": "IPV4"}

    # can't query the id until created, so construct "manually": 
    frontendIpConfId = ("/subscriptions/" + subscriptionId + "/resourceGroups/" + resourceGroupName + "/providers/Microsoft.Network/loadBalancers/" + loadbalancerName + "/frontendIPConfigurations/" + loadbalancerFrontEndIpConfName)

    logger.debug("front end IP config ID: {}".format(frontendIpConfId))

    #backendIpConf = {"name": "loadBalancerBackEndIpConf",
    #                 "private_ip_allocation_method": "Dynamic",
    #                 "private_ip_address_version": "IPV4"}

    backendAddrPool = {"name": "loadBalancerBackEndPool"}

    inboundNATRule1 = {"name": "vmssNAT1", "frontend_ip_configuration": {"id": frontendIpConfId},
                      "protocol": "Tcp", "frontend_port": 50001, "backend_port": 22,
                       "idle_timeout_in_minutes": 4, "enable_floating_ip": False,
                       "enable_tcp_reset": False
                      }

    inboundNATRule2 = {"name": "vmssNAT2", "frontend_ip_configuration": {"id": frontendIpConfId},
                       "protocol": "Tcp", "frontend_port": 50002, "backend_port": 22,
                       "idle_timeout_in_minutes": 4, "enable_floating_ip": False,
                       "enable_tcp_reset": False}

    inboundNATPool = {"name": "vmssNATPool", "frontend_ip_configuration": {"id": frontendIpConfId},
                       "frontend_port_range_start": 50000, "frontend_port_range_end": 50119, "backend_port": 22,
                       "protocol": "Tcp", "idle_timeout_in_minutes": 4,
                       "enable_floating_ip": False, "enable_tcp_reset": False}

    lbDict = {"location": "westus2", "sku": {"name": "Standard"},
             #"front_end_ip_configurations": [frontendIpConf],
              "frontendIPConfigurations": [frontendIpConf],
              "backend_address_pools": [backendAddrPool],
              "load_balancing_rules": [], "probes": [],
              "inbound_nat_rules": [inboundNATRule1, inboundNATRule2],
              "inbound_nat_pools": [inboundNATPool],
              "outbound_rules" : []
              }
    logger.debug("lb params: {}".format(lbDict))

    loadBalancer = networkClient.load_balancers.begin_create_or_update(
        resourceGroupName, loadbalancerName, lbDict).result()

    print("Load Balancer: {}".format(loadBalancer))

    logger.debug("backend pool id: {}".format(loadBalancer.backend_address_pools[0].id))
    logger.debug("nat pool id: {}".format(loadBalancer.inbound_nat_pools[0].id))

    vmssNATPoolId =  loadBalancer.inbound_nat_pools[0].id
    loadBalancerBackEndPoolId = loadBalancer.backend_address_pools[0].id

    computeClient = createComputeClient(subscriptionId, credential)
    serverimageReferenceId = "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Compute/images/%s" % (
        subscriptionId, imageResourceGroupName, serverimageName)
    clientimageReferenceId = "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Compute/images/%s" % (
        subscriptionId, imageResourceGroupName, clientimageName)

    vmDict = {
        "location": "westus2",
        "hardware_profile": {"vm_size": "Standard_D2_v2"},
        "storage_profile": {"image_reference": {"id": serverimageReferenceId}},
        #       "storage_profile":{"image_reference": { "publisher": 'Canonical',"offer": "UbuntuServer", "sku": "16.04.0-LTS", "version": "latest"}},
        "os_profile": {"computer_name": vmName, "admin_username": adminUserName, "admin_password": adminPassword},
        "network_profile": {"network_interfaces": [{"id": nic.id}]},
    }

    vm = computeClient.virtual_machines.begin_create_or_update(
        resourceGroupName, vmName, vmDict).result()
    print("VM:%s" % vm)

#    computeClient.virtual_machines.begin_power_off(resourceGroupName, vmName).result()
#    computeClient.virtual_machines.begin_delete(resourceGroupName, vmName).result()
#    resourceClient.resource_groups.begin_delete(resourceGroupName).result()

    vmssDict = {
        "location": "westus2",
        "overprovision": True,
        "upgrade_policy": {"mode": "Manual"},
        "sku": {"name": "Standard_D2_v2", "tier": "Standard", "capacity": vmssInstances},
        "virtual_machine_profile": {
            "storage_profile": {"image_reference": {"id": clientimageReferenceId}},
            "os_profile": {"computer_name_prefix": vmssName, "admin_username": adminUserName, "admin_password": adminPassword},
            "network_profile": {"network_interface_configurations": [{
                "name": "vmssnic",
                "primary": True,
                "enable_accelerated_networking": True,
                "ip_configurations": [{
                    "name": "vmssipconfig",
                    "subnet": {"id": subnet.id},
                    #"public_ip_address_configuration": {"name": "vmssipconf"},
                    "private_ip_address_version": "IPv4",
                    "load_balancer_backend_address_pools": [{"id": loadBalancerBackEndPoolId}],
                    "load_balancer_inbound_nat_pools": [{"id": vmssNATPoolId}]
                }]
            }]
            }
        }
    }
    vmss = computeClient.virtual_machine_scale_sets.begin_create_or_update(
        resourceGroupName, vmssName, vmssDict).result()
    
    print("vmss: {}".format(vmss))


if __name__ == "__main__":
    main()
