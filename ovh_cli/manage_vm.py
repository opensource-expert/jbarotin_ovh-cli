# -*- encoding: utf-8 -*-
# aim of this script is to aim the creation of vm thought ovh
# we use the API only in the test project PREPROD

import ovh
import logging
import sys
from time import sleep
import traceback

from .secret import get_ovh_connection_setting, get_general

from .apiovh import get_project_id, disp, get_instance_id

logging.getLogger(__name__)


# type must be private or public
def get_instance_ip(client, serviceName, instanceId, type):
    for i in range(20):
        instances = client.get(f"/cloud/project/{serviceName}/instance")
        for instance in instances:
            if instance["id"] == instanceId:
                if instance["status"] != "BUILD":
                    for ip in instance['ipAddresses']:
                        if int(ip["version"]) == 4:
                            if ip['type'] == type:
                                return ip['ip']
                else:
                    print("state=BUILD...please wait")
                    sleep(5)


def get_instance_public_ip(client, serviceName, instanceId):
    return get_instance_ip(client, serviceName, instanceId, "public")


def get_instance_private_ip(client, serviceName, instanceId):
    return get_instance_ip(client, serviceName, instanceId, "private")


def get_image_id(client, serviceName, name, region):
    for image in client.get(f"/cloud/project/{serviceName}/image"):
        if image["name"] == name and image["region"] == region:
            return image["id"]
    raise ReferenceError()


def get_flavor_id(client, serviceName, name, region):
    url = f"/cloud/project/{serviceName}/flavor"
    flavors = client.get(url)
    for flavor in flavors:
        if flavor["name"] == name and flavor["region"] == region:
            return flavor["id"]


def args(argv, inventary_file):
    actions = ["create", "delete", "connect_to_public", "reboot"]
    flavors = ["s1-2", "s1-4", "s1-8", "b2-30"]
    try:
        if argv[1] not in actions:
            raise Exception("Unknown action")
        elif argv[1] == "create":
            if argv[3] not in flavors:
                raise Exception("Unknown flavor")


    except Exception as e:
        print(e)
        traceback.print_exc()
        print("""python3 {} OPTION
        OPTION can be :
        - create VM_NAME FLAVOR [GROUP]
            FLAVOR can be {}
        - delete VM_NAME
        - connect_to_public VM_NAME
        - reboot VM_NAMES
        """.format(argv[0], flavors))
        return False
    return True


def create_vm(client, c_create, serviceName, base_distrib, region, flavor, vm_name, ssh_key_id, private_network_id,
              public_network_id):
    imageId = get_image_id(client, serviceName, base_distrib, region)
    flavorId = get_flavor_id(client, serviceName, flavor, region)

    return c_create.post(f"/cloud/project/{serviceName}/instance",
                         flavorId=flavorId,  # Instance flavor id (type: string)
                         groupId=None,  # Start instance in group (type: string)
                         imageId=imageId,
                         monthlyBilling=False,  # Active monthly billing (type: boolean)
                         name=vm_name,
                         networks=[{'ip': None, 'networkId': private_network_id},
                                   {'ip': None, 'networkId': public_network_id}],
                         region=region,  # Instance region (type: string)
                         sshKeyId=ssh_key_id,  # SSH keypair id (type: string)
                         userData=None,  # Configuration information or scripts to use upon launch (type: text)
                         volumeId=None)  # Specify a volume id to boot from it (type: string))


def delete_vm(client, c_create, serviceName, vm_name):
    instanceId = get_instance_id(client, serviceName, vm_name)
    disp(c_create.delete(f"/cloud/project/{serviceName}/instance/{instanceId}"))


def connect_instance_to_network(client, c_create, serviceName, vm_name, networkId):
    instanceId = get_instance_id(client, serviceName, vm_name)
    result = c_create.post(f'/cloud/project/{serviceName}/instance/{instanceId}/interface',
                           ip=None,
                           networkId=networkId)


def reboot(c_create, serviceName, vm_names):
    for vm_name in vm_names:
        instanceId = get_instance_id(c_create, serviceName, vm_name)
        result = c_create.post(f'/cloud/project/{serviceName}/instance/{instanceId}/reboot',
                               type="soft")


def main():
    manage(**get_general())


def manage(project_name, base_distrib, region, ssh_key_id, inventary_file, private_network_id, public_network_id):
    argv = sys.argv

    c_create = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting("vm")
    )

    client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting("get-info")
    )

    if args(argv, inventary_file):
        serviceName = get_project_id(client, project_name)
        vm_name = argv[2]
        if argv[1] == "create":
            flavor = argv[3]
            # flavor sandbox
            # "s1-2" 1 vcore, RAM : 2GB, 10GB disk
            # "s1-4" 1 vcore, RAM : 4GB, 20GB disk
            # "s1-8" 2 vcore, RAM : 8GB, 40GB disk
            vm = create_vm(client, c_create, serviceName, base_distrib, region, flavor, vm_name, ssh_key_id,
                           private_network_id, public_network_id)
            # disp(vm)
            ip = get_instance_public_ip(client, serviceName, vm["id"])
            print(ip)
            ip_private = get_instance_private_ip(client, serviceName, vm["id"])

        elif argv[1] == "delete":
            delete_vm(client, c_create, serviceName, vm_name)
            # delete_instance_to_inventory(inventary_file, vm_name)

        elif argv[1] == "connect_to_public":
            connect_instance_to_network(client, c_create, serviceName, vm_name, public_network_id)

        elif argv[1] == "reboot":
            reboot(c_create, serviceName, vm_name.split(","))


if __name__ == "__main__":
    main()
