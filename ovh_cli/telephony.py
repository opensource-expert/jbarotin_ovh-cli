#!/usr/local/bin/python3
# -*- encoding: utf-8 -*-


import ovh
import sys

from ovh_cli.secret import get_ovh_connection_setting
from ovh_cli.apiovh import disp


def account(client):
    for serviceName in client.get("/telephony/"):
        print(serviceName)
        print(f"/telephony/{serviceName}")
        disp(client.get(f"/telephony/{serviceName}/"))


def service(client):
    disp(client.get(f"/telephony/{billingAccount}/service"))


def event(client):
    for serviceName in client.get(f"/telephony/{billingAccount}/service"):
        print(serviceName)
        disp(client.get(f"/telephony/{billingAccount}/service/{serviceName}/diagnosticReports",
                        dayInterval="today"))


def create_token(client, serviceName):
    disp(client.post(f"/telephony/{billingAccount}/service/{serviceName}/eventToken",
                     expiration='unlimited'
                     ))


billingAccount = "my-billing-account"


def main():
    client = ovh.Client(
        endpoint='ovh-eu',  # Endpoint of API OVH Europe (List of available endpoints)
        **get_ovh_connection_setting("telephony")
    )

    if sys.argv[1] == "account":
        account(client)
    elif sys.argv[1] == "event":
        event(client)
    elif sys.argv[1] == "service":
        service(client)
    elif sys.argv[1] == "create_token":
        create_token(client, sys.argv[2])


if __name__ == "__main__":
    main()
