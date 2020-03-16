# OVH CLI 


## Presentation 
*Beta application use it at your own risk*

Aim of this app, is to provide an administration command line that aim to access to ovh services thought the API (https://api.ovh.com/).


## Quick start

### Prerequisite

* Python 3

### Installation 

There's only two dependency (request & ovh), so you can install it in your main repo. 

```
git clone <urlofthisrepo>
cd ovh-cli
pip install --user -r requirements.txt
pip install --user .
```


## Get your OVH information in command line 

You'll need credential api that have read only on all your OVH world.

Edit the file `~/.ovh-cli/secret` and add the following section

```
[general]
project_name = <project_name>

[get-info]
application_key = <application_key>
application_secret = <application_secret>
consumer_key = <consumer_key>
```

project_name is the name of the ovh public_cloud project you'd like to interact by default with the API.

Then, use this command line `ovh-get-info`, it will display all the argument you can query. 

## Manage VM though command line


Edit the file `~/.ovh-cli/secret`

```

[general]
project_name = <project_name>
base_distrib = <base distrib you want in your VM>
region = <OVH region>
ssh_key_id = <uuid of you ssh key>
private_network_id = <private network id>
public_network_id = <public network id>



[vm]
application_key = <application_key>
application_secret = <application_secret>
consumer_key = <consumer_key>
```

With :
- project_name : name of the OVH projet where you want to manage your VM
- base_distrib : name of the distribution you want installed by default on your new VM, list is available thought `ovh-get-info image`
- region :  name of the ovh region to use, list available thought (`ovh-get-info regions`)
- ssh_key_id : id of the ssh key to be installed on a new vm (`ovh-get-info ssh_key`)
- private_network_id : id the vrack you want that vm to be connected (`ovh-get-info private_network`)
- public_network_id : default id of the public network connection (`ovh-get-info public_network`)

