import requests
import urllib3
import time
import json
import re
from getpass import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONTROLLER_FQDN="https://nginxcontroller.westeurope.cloudapp.azure.com"
def main_procedure():
    user=""
    passw=""
    session = auth_controller(user, passw)
    endpoint = "/api/v1/infrastructure/locations/unspecified/instances"
    endpoint = CONTROLLER_FQDN+endpoint
    headers = { 'content-type': "application/json" }
    response = (session.get(endpoint, headers=headers, verify=False).text)
    offline_ins = find_offline_instances(response)
    delete_offline_instance(offline_ins,session)


def find_offline_instances(response):
    offline_ins = []
    array_json = []
    xline = []
    words = json.loads(response)
    array_json = json.dumps(words, indent=4, sort_keys=True)
    array_json = array_json.split('"currentStatus":')
    for xline in array_json:
        founded = False
        if xline.find('"online": false,') != -1 and founded == False:
            xline = xline.splitlines()
            for line in xline:
                if line.find('"ref":') != -1 and founded == False:
                    tmp = line.split('"')
                    for i in tmp:
                        if i.find('/infrastructure/locations/unspecified/instances/') != -1 and founded == False:
                            offline_ins.append(i)
                            founded = True
    return(offline_ins)


def delete_offline_instance(offline_ins,session):
    x = 0
    for i in offline_ins:
        endpoint = CONTROLLER_FQDN+'/api/v1'+i
        headers = { 'content-type': "application/json" }
        response = session.delete(endpoint, headers=headers, verify=False)
        if (200 <= response.status_code <= 210):
            i = i.split('/')
            y = len(i)
            print("delete instance:", i[y-1])
            x += 1
        else:
            print("error delete instance", i)
        time.sleep(2)
    print("number of instances were deleted:",x)

                                       
def auth_controller(u, p):
    if len(u)==0 or len(u)==0:
        u = input("Enter username: ")
        p = getpass("Enter password: ")

    endpoint = "/api/v1/platform/login"
    endpoint = CONTROLLER_FQDN+endpoint
    payload = """
    {
    "credentials": {
        "type": "BASIC",
        "username": "xxxxusernamexxxx",
        "password": "xxxxpasswordxxxx"
    }
    }
    """
    payload = payload.replace("xxxxusernamexxxx",u)
    payload = payload.replace("xxxxpasswordxxxx",p)
    headers = { 'content-type': "application/json" }
    session = requests.session()
    response = session.post(endpoint, data=payload, headers=headers, verify=False)
    if (200 <= response.status_code <= 210):
        print("login successful")
    else:
        print("Try to login again.....")
    return session

main_procedure()