# -*- encoding: utf-8 -*-
# aim of this script is to query different parameter of our OVH account

import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import ovh
import logging
import socket

from .apiovh import get_project_id, disp, get_instance_name

from .secret import get_ovh_connection_setting, get_general

logging.getLogger(__name__)


def get_public_ip_v4(instance):
    for ip in instance['ipAddresses']:
        if int(ip["version"]) == 4 and ip["type"] == "public":
            return ip["ip"]
    raise ReferenceError()


def display_distrib(client, serviceName):
    for image in client.get(f"/cloud/project/{serviceName}/image"):
        # disp(image)
        print("- '{}' {} {}".format(image["name"], image["region"], image["id"]))


def display_instances(client, serviceName):
    instances = client.get(f"/cloud/project/{serviceName}/instance")
    for instance in instances:
        print("- '{}' '{}' {}".format(instance['name'], instance['id'], instance["status"]))
        for ip in instance['ipAddresses']:
            if int(ip["version"]) == 4:
                network = ""
                if ip['type'] == "private":
                    network = ip['networkId']
                print("\t- ip : {} {} {}".format(ip['ip'], ip['type'], network))


def display_regions(client, serviceName):
    url = f"/cloud/project/{serviceName}/region"
    for region in client.get(url):
        disp(region)


def display_foips(client, serviceName):
    url = f"/cloud/project/{serviceName}/ip/failover"
    for ip in client.get(url):
        try:
            ns_list = socket.gethostbyaddr(ip["ip"])
        except:
            ns_list = ["unknown"]

        ns = ""
        if len(ns_list) > 0:
            ns = ns_list[0]
        print("- ip '{}' routedTo '{}' nsresolve : '{}'".format(ip["ip"],
                                                                get_instance_name(client, serviceName, ip["routedTo"]),
                                                                ns))


def display_ssh_key(client, serviceName):
    disp(client.get(f"/cloud/project/{serviceName}/sshkey"))


def tab(value):
    if len(value) < 8:
        return "\t"
    else:
        return ""


def display_flavor(client, serviceName):
    url = f"/cloud/project/{serviceName}/flavor"
    flavors = client.get(url)
    print("This all the flavor of VM available in linux and SBG3")
    print("region\tname\t\tvcpus\tdisk\tram\tavailable\tid")
    for flavor in flavors:
        if flavor["osType"] == "linux" and flavor["region"] in ["SBG3", "GRA1"]:
            print("{}\t{}\t{}{}\t{}\t{}GB\t{}\t{}".format(flavor["region"],
                                                          flavor["name"],
                                                          tab(flavor["name"]),
                                                          flavor["vcpus"],
                                                          flavor["disk"],
                                                          flavor["ram"] / 1000,
                                                          flavor["available"],
                                                          flavor["id"]))


def display_group(client, serviceName):
    url = f"/cloud/project/{serviceName}/instance/group"
    disp(client.get(url))


def display_cloud_project(client, serviceName):
    url = f"/cloud/project"
    for key in client.get(url):
        disp(client.get(url + "/" + key))


def display_private_networks(client, serviceName):
    url = f"/cloud/project/{serviceName}/network/private"
    for network in client.get(url):
        print("- name: '{}' vlanId : '{}' id: {}".format(network["name"], network["vlanId"], network["id"]))
        # disp(network)
        for subnet in client.get("/cloud/project/{}/network/private/{}/subnet".format(serviceName, network["id"])):
            print("\t* subnet '{}' id : '{}'".format(subnet["cidr"], subnet["id"]))
            for ipPool in subnet["ipPools"]:
                print("\t\t> region: {} dchp: '{}' start: '{}' end: '{}'".format(ipPool["region"], ipPool["dhcp"],
                                                                                 ipPool["start"], ipPool["end"]))


def display_public_networks(client, serviceName):
    url = f"/cloud/project/{serviceName}/network/public"
    disp(client.get(url))


def display_me(client, serviceName):
    disp(client.get("/me"))


def display_vrack(client, serviceName):
    disp(client.get("/vrack"))


def display_allowed_service(client, serviceName):
    disp(client.get(f"/vrack/pn-1045553/allowedServices"))


def display_ip(client, serviceName):
    url = f"/cloud/project/{serviceName}/ip"
    disp(client.get(url))


def display_dns_zone(client, nope):
    for zone in client.get("/domain/zone"):
        print(zone)
        for record in client.get(f"/domain/zone/{zone}/record"):
            disp(client.get(f"/domain/zone/{zone}/record/{record}"))


def display_nasha(client, nope):
    for servicename in client.get("/dedicated/nasha"):

        # disp(client.get(f"/dedicated/nasha/{servicename}/use"))
        detail = client.get(f"/dedicated/nasha/{servicename}")
        print("{} ip : {} datacenter: {}".format(servicename, detail["ip"], detail["datacenter"]))
        for partition_name in client.get(f"/dedicated/nasha/{servicename}/partition"):
            print(f"\t- {partition_name}")
            url = f"/dedicated/nasha/{servicename}/partition/{partition_name}/use"
            used_detail = client.get(url, type='used')
            print("\t\tused={}{}".format(used_detail["value"], used_detail["unit"]))
            size_detail = client.get(url, type='size')
            print("\t\tsize={}{}".format(size_detail["value"], size_detail["unit"]))
            snap_detail = client.get(url, type='usedbysnapshots')
            print("\t\tusedbysnapshot={}{}".format(snap_detail["value"], snap_detail["unit"]))


cmd = {
    "images": ("List all iso images available to initialize an instance", display_distrib),
    "ipfailover": ("List all ipfailover", display_foips),
    "instances": ("List all instances created", display_instances),
    "regions": ("List all geographical ovh regions ", display_regions),
    "flavor": ("List all type of VM", display_flavor),
    "group": ("Groups of instances", display_group),
    "cloud_projects": ("List of public cloud project", display_cloud_project),
    "private_network": ("Display information about private network", display_private_networks),
    "public_network": ("Display information about internet connection (public)", display_public_networks),
    "ssh_key": ("Display the list of ssh key", display_ssh_key),
    "ip": ("Display ip", display_ip),
    "me": ("Display information about the current account", display_me),
    "vrack": ("Display information about vrack", display_vrack),
    "allowedServices": ("Display allowed services in vRack", display_allowed_service),
    "dns_zone": ("Display dns zone", display_dns_zone),
    "nasha": ("Display nas ha detaile", display_nasha)
}


def usage():
    print("python3 ovh-api.py <option>")
    print("where option can be : ")
    for c in cmd:
        print("- " + c + " : " + cmd[c][0])


def get_infos(project_name):
    client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting()
    )

    serviceName = get_project_id(client, project_name)
    argv = sys.argv
    try:
        cmd[argv[1]]
    except (KeyError, IndexError):
        usage()
        return

    cmd[argv[1]][1](client, serviceName)


def main():
    config = get_general()
    get_infos(config["project_name"])

if __name__ == "__main__":
    main()
