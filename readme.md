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

Edit the file `~/.ovh-cli/secret`

```
[get-info]
application_key = <application_key>
application_secret = <application_secret>
consumer_key = <consumer_key>
```

Then, use this command line `ovh-get-info`, it will display all the argument you can query. 

