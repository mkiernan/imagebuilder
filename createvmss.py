# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import random
import string
import logging
import base64
import time

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

    #-- register the task absolute start time (for 3.7 use time.time_ns())
    launch=time.time()

    subscriptionId = os.environ.get("SUBSCRIPTION_ID", None)
    credential = DefaultAzureCredential()
    location = 'southcentralus'
    resourceGroupName = "mktmpgrp"
    imageResourceGroupName = "mkimagegrp"
    subnetName = "compute"
    interfaceName = "interfaceName"
    networkName = "gridvnet"
    adminUserName = "adminUserName"
    adminPassword = "<YOUR PASSWORD>"

    serverimageName = "redisserverImage"
    clientimageName = "redisclientImage"
    vmName = "redisserver"
    vmssName = "redisclient"
    vmssInstances = 2
    nsgName = "vmssnsg"
    loadbalancerName = "vmssloadbalancer"
    loadbalancerFrontEndIpConfName = "loadBalancerFrontEnd"

    resourceClient = createResourceClient(subscriptionId, credential)

    resourceDict = {'location': location}
    resourceClient.resource_groups.create_or_update(
        resourceGroupName, resourceDict)

    networkClient = createNetworkClient(subscriptionId, credential)

    vnetDict = {'location': location, 'address_space': {
        'address_prefixes': ['10.0.0.0/16']}}
    vnet = networkClient.virtual_networks.begin_create_or_update(
        resourceGroupName, networkName, vnetDict).result()

    subnetDict = {'address_prefix': '10.0.0.0/22'}
    subnet = networkClient.subnets.begin_create_or_update(
        resourceGroupName, networkName, subnetName, subnetDict).result()

    sshRule = {"name": "default-allow-ssh", "protocol": "Tcp", "source_port_range": "*",
               "destination_port_range": "22", "source_address_prefix": "*", 
               "destination_address_prefix": "*", "access": "Allow", "priority": 1000,
               "direction": "Inbound", "source_port_ranges": [], "destination_port_ranges": [],
               "source_address_prefixes": [], "destination_address_prefixes": []
    }
    redisRule = {"name": "open-6379-80-redis", "protocol": "Tcp", "source_port_range": "*",
               "destination_port_range": "6379-6380", "source_address_prefix": "*", 
               "destination_address_prefix": "*", "access": "Allow", "priority": 900,
               "direction": "Inbound", "source_port_ranges": [], "destination_port_ranges": [],
               "source_address_prefixes": [], "destination_address_prefixes": []
    }
    nsgDict = {"id": nsgName, "location": location, "security_rules": [sshRule,redisRule]}
    nsg = networkClient.network_security_groups.begin_create_or_update(
        resourceGroupName, networkName, nsgDict).result()
    logger.debug("NSG: %s" % nsg)
    logger.debug("NSG.id: %s" % nsg.id)

    publicIpDict = {"location": location, "public_ip_allocation_method": "Static",
                    "public_ip_address_version": "IPV4", "sku": {"name": "Standard"}}
    publicIp = networkClient.public_ip_addresses.begin_create_or_update(
        resourceGroupName, "public_ip_address_name", publicIpDict).result()

    nicDict = {'location': location,
               'ip_configurations': [{
                   'name': 'ipconfig', 'subnet': {'id': subnet.id}, 
                   "public_ip_address": {"id": publicIp.id},
                   "private_ip_allocation_method": "Dynamic"
                   }],
        "enableAcceleratedNetworking": True, 
        "network_security_group": {"id": nsg.id},
    }

    nic = networkClient.network_interfaces.begin_create_or_update(
        resourceGroupName, interfaceName, nicDict).result()
    logger.debug("NIC:%s" % nic)

    # -- create load balancer for vmss
    lbpublicIpDict = {"location": location, "public_ip_allocation_method": "Static",
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
                       "enable_tcp_reset": False}

    inboundNATRule2 = {"name": "vmssNAT2", "frontend_ip_configuration": {"id": frontendIpConfId},
                       "protocol": "Tcp", "frontend_port": 50002, "backend_port": 22,
                       "idle_timeout_in_minutes": 4, "enable_floating_ip": False,
                       "enable_tcp_reset": False}

    inboundNATPool = {"name": "vmssNATPool", "frontend_ip_configuration": {"id": frontendIpConfId},
                       "frontend_port_range_start": 50000, "frontend_port_range_end": 50119, "backend_port": 22,
                       "protocol": "Tcp", "idle_timeout_in_minutes": 4,
                       "enable_floating_ip": False, "enable_tcp_reset": False}

    lbDict = {"location": location, "sku": {"name": "Standard"},
             #"front_end_ip_configurations": [frontendIpConf],
              "frontendIPConfigurations": [frontendIpConf],
              "backend_address_pools": [backendAddrPool],
              "load_balancing_rules": [], "probes": [],
#              "inbound_nat_rules": [inboundNATRule1, inboundNATRule2],
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
        "location": location,
        "hardware_profile": {"vm_size": "Standard_D2_v2"},
        "storage_profile": {"image_reference": {"id": serverimageReferenceId}},
        #       "storage_profile":{"image_reference": { "publisher": 'Canonical',"offer": "UbuntuServer", "sku": "16.04.0-LTS", "version": "latest"}},
        "os_profile": {"computer_name": vmName, "admin_username": adminUserName, "admin_password": adminPassword},
        "network_profile": {"network_interfaces": [{"id": nic.id}]},
    }
    start=time.perf_counter()
    vm = computeClient.virtual_machines.begin_create_or_update(
        resourceGroupName, vmName, vmDict).result()
    end=time.perf_counter()
    timedelta=end-start
    print("VM:%s" % vm)
    print("VM Provision Time: {}",timedelta)
    

#    computeClient.virtual_machines.begin_power_off(resourceGroupName, vmName).result()
#    computeClient.virtual_machines.begin_delete(resourceGroupName, vmName).result()
#    resourceClient.resource_groups.begin_delete(resourceGroupName).result()

    with open("cloud-init.txt") as f:
         res = f.read()
    xstr = base64.b64encode(res.encode('utf-8')).decode('ascii')

    vmssDict = {
        "location": location,
        "overprovision": True,
        "upgrade_policy": {"mode": "Manual"},
        "sku": {"name": "Standard_HB120rs_v2", "tier": "Standard", "capacity": vmssInstances},
        "virtual_machine_profile": {
            "storage_profile": {"image_reference": {"id": clientimageReferenceId}},
            "priority": "Spot",
            "eviction_policy": "Delete",
            "billing_profile": {"max_price": -1 },
            "os_profile": {
                "computer_name_prefix": vmssName,
                "admin_username": adminUserName,
                "admin_password": adminPassword,
                "custom_data": xstr 
            },
            "network_profile": {"network_interface_configurations": [{
                "name": "vmssnic",
                "primary": True,
                "enable_accelerated_networking": False,
                "network_security_group": {"id": nsg.id},
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

    start=time.perf_counter()
    vmss = computeClient.virtual_machine_scale_sets.begin_create_or_update(
        resourceGroupName, vmssName, vmssDict).result()
    end=time.perf_counter()
    timedelta=end-start
    print("vmss: {}".format(vmss))
    print("VMSS Provision Time: {}",timedelta)

if __name__ == "__main__":
    main()
