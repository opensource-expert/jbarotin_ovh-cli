# -*- encoding: utf-8 -*-

import json

def get_project_id(client, name):
    projects_keys = client.get('/cloud/project')
    #print(projects_keys)
    for key in projects_keys :
        project = client.get('/cloud/project/' + key)
        if project["description"] == name:
            return key

    raise ReferenceError()


def disp(dump):
    print(json.dumps(dump, indent=4))


def get_instance_id(client, serviceName, vm_name):
    instances = client.get(f"/cloud/project/{serviceName}/instance")
    for instance in instances:
        if instance["name"] == vm_name:
            return instance["id"]


def get_instance_name(client, serviceName, vm_id):
    instances = client.get(f"/cloud/project/{serviceName}/instance")
    for instance in instances:
        if instance["id"] == vm_id:
            return instance["name"]
