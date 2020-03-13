# -*- encoding: utf-8 -*-

import requests
import sys
import json

def __get_key(app_key, authorisation):
    data = '{{ "accessRules":  {json_data}  }}'.format(json_data = json.dumps(authorisation))
    # print(data)

    r = requests.post("https://eu.api.ovh.com/1.0/auth/credential",
                        headers = {
                            "X-Ovh-Application" : app_key,
                            "Content-type" : "application/json"
                        },
                        data = data)

    print(r.content)

# this file provide ovh credential to admin
# dns entry point
def dns(app_key, dns_list):

    authorisation = []
    for dns in dns_list.split(","):
        authorisation.append({ "method" : "POST", "path": f"/domain/zone/{dns}/*" })
        authorisation.append({ "method" : "DELETE", "path": f"/domain/zone/{dns}/*" })

    __get_key(app_key, authorisation)


def network(app_key, projects_list):
    authorisation = []
    for serviceName in projects_list.split(","):
        authorisation.append({ "method" : "GET", "path": f"/cloud/project/{serviceName}/instance" })
        authorisation.append({ "method" : "POST", "path": f"/cloud/project/{serviceName}/ip/*" })
        authorisation.append({ "method" : "GET", "path": f"/cloud/project/{serviceName}/ip/*" })
    __get_key(app_key, authorisation)

def telephony(app_key, projects_list):
    authorisation = []
    authorisation.append({ "method" : "GET", "path": f"/telephony/*" })
    for billingAccount in projects_list.split(","):
        authorisation.append({ "method" : "POST", "path" : f"/telephony/{billingAccount}/service/*"})
        authorisation.append({ "method" : "POST", "path" : f"/telephony/{billingAccount}/eventToken"})

    __get_key(app_key, authorisation)

def usage():
    print("""usage OPTION ...
OPTIONS can be :
- dns app_key dns1[,dns2...]
- network app_key project1[,project2...]
- telephony app_key
""")

def main():
    if len(sys.argv) == 4 :
        if sys.argv[1] == "dns":
            dns(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "network":
            network(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "telephony":
            telephony(sys.argv[2], sys.argv[3])
        else:
            usage()

    else:
        usage()


if __name__ == "__main__":
    main()
