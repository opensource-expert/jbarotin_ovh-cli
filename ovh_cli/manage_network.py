# -*- encoding: utf-8 -*-
# aim of this script is to aim the creation of vm thought ovh


import ovh
import logging
import sys
from time import sleep
import traceback

from .secret import get_ovh_connection_setting

from .apiovh import get_project_id, disp, get_instance_id

logging.getLogger(__name__)


# uncomment to enable logging of all http requests
# import http.client
# http.client.HTTPConnection.debuglevel = 1
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

def get_foips_id(client, serviceName, sip):
    url = f"/cloud/project/{serviceName}/ip/failover"
    for ip in client.get(url):
        if ip["ip"] == sip:
            return ip["id"]
    raise Exception("Not found")


def rename(client, serviceName, networkId, newName):
    url = f"/cloud/project/{serviceName}/network/private/{networkId}"
    disp(client.put(url, name=newName))


# def create_dynamic_subnet(client, serviceName, networkId, start, end, network, region):
#     return create_subnet(client, serviceName, networkId, start, end, network, region, True)
#
# def create_static_subnet(client, serviceName, networkId, start, end, network, region):
#     return create_subnet(client, serviceName, networkId, start, end, network, region, False)

def create_subnet(client, serviceName, networkId, start, end, network, region, dhcp):
    disp(client.post(f"/cloud/project/{serviceName}/network/private/{networkId}/subnet",
                     dhcp=dhcp,  # Enable DHCP (type: boolean)
                     start=start,  # First IP for this region (eg: 192.168.1.12) (type: ip)
                     end=end,  # Last IP for this region (eg: 192.168.1.24) (type: ip)
                     network=network,  # Global network with cidr (eg: 192.168.1.0/24) (type: ipBlock)
                     noGateway=False,  # Set to true if you don't want to set a default gateway IP (type: boolean)
                     region=region  # Region where this subnet will be created (type: string)
                     ))


def delete_subnet(client, serviceName, networkId, subnetId):
    disp(client.delete(f"/cloud/project/{serviceName}/network/private/{networkId}/subnet/{subnetId}"))


def delete(client, serviceName, networkId):
    url = f"/cloud/project/{serviceName}/network/private/{networkId}"
    print(url)
    disp(client.delete(url))


def create_network(client, serviceName, name, region, vlanId):
    print(vlanId)
    print(region)
    print(name)
    disp(client.post(f"/cloud/project/{serviceName}/network/private",
                     name=name,  # Network name (type: string)
                     regions=[region],
                     # Region where to activate private network. No parameters means all region (type: string[])
                     vlanId=vlanId  # Vland id, between 0 and 4000. 0 value means no vlan. (type: long)
                     ))


def attach_failover(client, serviceName, instance_name, ip):
    instance_id = get_instance_id(client, serviceName, instance_name)
    id = get_foips_id(client, serviceName, ip)
    url = f"/cloud/project/{serviceName}/ip/failover/{id}/attach"
    print(url)
    disp(client.post(url, instanceId=instance_id))


def usage(argv):
    cmd = {"rename": 4,
           "create_subnet": 7,
           "delete_subnet": 4,
           "delete": 3,
           "create": 4,
           "attach_failover": 5
           }

    try:
        if argv[1] in cmd:
            if len(argv) != cmd[argv[1]]:
                raise Exception("Wrong number of arguments")
        else:
            raise Exception("Unknown action")
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("""python3 {0} OPTION
        OPTION can be :
        - create NAME VLANID
        - delete NETWORK_ID
        - rename NETWORK_ID NEW_NAME
        - delete_subnet NETWORK_ID SUBNETID
        - create_subnet NETWORK_ID START_IP END_IP NETWORK DHCP
            With START_IP is minimum XXX.XXX.XXX.2
            NETWORK is something like 10.56.1.0/24
            DHCP is dhcp or static
        - attach_failover INSTANCE_NAME IP PROJECT
        example of command:
        python {0} create_subnet pn-1045553_1500 10.56.1.100 10.56.1.200 "10.56.1.0/24" dhcp
        """.format(argv[0]))
        return False
    return True


def main():
    argv = sys.argv
    # test env
    project_name = "PREPROD"
    region = "SBG3"

    read_client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting()
    )

    create_client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting("network")
    )

    if usage(sys.argv):
        serviceName = get_project_id(read_client, project_name)
        if argv[1] == "rename":
            rename(create_client, serviceName, argv[2], argv[3])
        elif argv[1] == "create_subnet":
            if argv[6] == "dhcp":
                create_subnet(create_client, serviceName, argv[2], argv[3], argv[4], argv[5], region, True)
            else:
                create_subnet(create_client, serviceName, argv[2], argv[3], argv[4], argv[5], region, False)
        elif argv[1] == "delete_subnet":
            delete_subnet(create_client, serviceName, argv[2], argv[3])
        elif argv[1] == "delete":
            delete(create_client, serviceName, argv[2])
        elif argv[1] == "create":
            create_network(create_client, serviceName, argv[2], region, int(argv[3]))
        elif argv[1] == "attach_failover":
            serviceName = get_project_id(read_client, argv[4])
            attach_failover(create_client, serviceName, argv[2], argv[3])


if __name__ == "__main__":
    main()
