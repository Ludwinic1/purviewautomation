import json
import os

import requests

CLIENT_ID = os.environ["CLIENTID"]
CLIENT_SECRET = os.environ["CLIENTSECRET"]
TENANT_ID = os.environ["TENANT_ID"]
SUB_ID = os.environ["SUB_ID"]
RG_NAME = os.environ["RG_NAME"]
PURVIEW_ACCOUNT_NAME = os.environ["PURVIEW_ACCOUNT_NAME"]
LOCATION = os.environ["LOCATION"]

url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token"
header = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
    "resource": "https://purview.azure.net/",
}
access_token_request = requests.get(url=url, headers=header, data=data)
access_token = access_token_request.json()["access_token"]

url = f"https://management.azure.com/subscriptions/{SUB_ID}/resourceGroups/{RG_NAME}/providers/Microsoft.Purview/accounts/{PURVIEW_ACCOUNT_NAME}?api-version=2021-07-01"
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
data = {"location": LOCATION}
create_purview_request = requests.put(url=url, headers=headers, data=json.dumps(data))
