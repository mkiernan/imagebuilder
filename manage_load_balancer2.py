# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient


def main():

    SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", None)
    GROUP_NAME = "mktmpgrp3"
    LOAD_BALANCER_NAME = LOAD_BALANCER = "load_balancerxxyyzz"
    PUBLIC_IP_ADDRESS_NAME = "public_ip_address_name"
    FRONTEND_IPCONFIGURATION_NAME = "myFrontendIpconfiguration"
    BACKEND_ADDRESS_POOL_NAME = "myBackendAddressPool"
    LOAD_BALANCING_RULE_NAME = "myLoadBalancingRule"
    OUTBOUND_RULE_NAME = "myOutboundRule"
    PROBE_NAME = "myProbe"

    # Create client
    # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resource_client = ResourceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=SUBSCRIPTION_ID
    )
    network_client = NetworkManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=SUBSCRIPTION_ID
    )

    # Create resource group
    resource_client.resource_groups.create_or_update(
        GROUP_NAME,
        {"location": "westus2"}
    )

    # - init depended resources -
    # Create public ip address
    network_client.public_ip_addresses.begin_create_or_update(
        GROUP_NAME,
        PUBLIC_IP_ADDRESS_NAME,
        {
            'location': "westus2",
            'public_ip_allocation_method': 'Static',
            'idle_timeout_in_minutes': 4,
            'sku': {
              'name': 'Standard'
            }
        }
    ).result()
    # - end -

    # Create load balancer
    load_balancer = network_client.load_balancers.begin_create_or_update(
        GROUP_NAME,
        LOAD_BALANCER,
        {
          "location": "westus2",
          "sku": {
            "name": "Standard"
          },
          "frontendIPConfigurations": [
            {
              "name": FRONTEND_IPCONFIGURATION_NAME,
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + GROUP_NAME + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME 
              }
            }
          ],
          "backend_address_pools": [
            {
              "name": BACKEND_ADDRESS_POOL_NAME
            }
          ],
        }
    ).result()
    print("Create load balancer:\n{}".format(load_balancer))

    # Get load balancer
    load_balancer = network_client.load_balancers.get(
        GROUP_NAME,
        LOAD_BALANCER
    )
    print("Get load balancer:\n{}".format(load_balancer))

    # Update load balancer
    load_balancer = network_client.load_balancers.update_tags(
        GROUP_NAME,
        LOAD_BALANCER,
        {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
    )
    print("Update load balancer:\n{}".format(load_balancer))
    
    # Delete load balancer
#    load_balancer = network_client.load_balancers.begin_delete(
#        GROUP_NAME,
#        LOAD_BALANCER
#    ).result()
#    print("Delete load balancer.\n")

    # Delete Group
#    resource_client.resource_groups.begin_delete(
#        GROUP_NAME
#    ).result()


if __name__ == "__main__":
    main()
