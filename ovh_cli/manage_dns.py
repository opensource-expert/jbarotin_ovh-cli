#!/usr/local/bin/python3
# -*- encoding: utf-8 -*-

import ovh
import sys

from .secret import get_ovh_connection_setting
from .apiovh import get_project_id, disp, get_instance_id


def __check_record(zone, subdomain, record):
    if zone != "" and zone not in record["zone"]:
        return False
    elif subdomain != "" and subdomain not in record["subDomain"]:
        return False
    else:
        return True


def display_dns_zone(client, zone, subdomain):
    for zone in client.get("/domain/zone"):
        print(zone)
        for id in client.get(f"/domain/zone/{zone}/record"):
            record = client.get(f"/domain/zone/{zone}/record/{id}")
            if __check_record(zone, subdomain, record):
                disp(record)


def get_dns_record_id(client, zoneName, subDomain, type):
    for zone in client.get("/domain/zone"):
        if zone == zoneName:
            for recordId in client.get(f"/domain/zone/{zoneName}/record"):
                record = client.get(f"/domain/zone/{zoneName}/record/{recordId}")
                if record["subDomain"] == subDomain and record["fieldType"] == type:
                    return recordId

    raise Exception(f"{zone}, {subDomain}, {type} not found")


def delete_dns(client, zoneName, subDomain, type):
    id = get_dns_record_id(client, zoneName, subDomain, type)
    url = f"/domain/zone/{zoneName}/record/{id}"
    print(url)
    disp(client.delete(url))
    disp(client.post(f"/domain/zone/{zoneName}/refresh"))


def create_dns(client, zoneName, subDomain, type, target):
    print(f"""/domain/zone/{zoneName}/record ,
                        subDomain = {subDomain},
                        fiedType = {type},
                        target = {target}""")
    disp(client.post(f"/domain/zone/{zoneName}/record",
                     subDomain=subDomain,
                     fieldType=type,
                     target=target))

    disp(client.post(f"/domain/zone/{zoneName}/refresh"))


def usage(argv):
    print("""USAGE : {} OPTION ARGS
    with OPTION :
    - display [ZONE_PATTERN] [SUBDOMAIN_PATTERN]
    - delete ZONE SUBDOMAIN TYPE TARGET
    - create ZONE SUBDOMAIN TYPE

    example :
        - ovh-manage-dns create mydomain.fr test TXT azerty
        - ovh-manage-dns display mydomain.fr
    """.format(argv[0]))


def main():
    argv = sys.argv
    client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting("dns")
    )

    if len(argv) == 1:
        usage(argv)
    elif argv[1] == "display":
        zone = ""
        subdomain = ""
        if len(argv) == 3:
            zone = argv[2]
        if len(argv) == 4:
            subdomain = argv[3]
        display_dns_zone(client, zone, subdomain)
    elif argv[1] == "delete":
        delete_dns(client, argv[2], argv[3], argv[4])
    elif argv[1] == "create":
        create_dns(client, argv[2], argv[3], argv[4], argv[5])
    else:
        usage(argv)


if __name__ == "__main__":
    main()
