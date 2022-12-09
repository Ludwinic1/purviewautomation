from purviewautomation import ServicePrincipalAuthentication

from azure.identity import AzureCliCredential

from purviewautomation import PurviewCollections, AzIdentityAuthentication

auth = AzIdentityAuthentication(credential=AzureCliCredential())

client = PurviewCollections(purview_account_name="yourpurviewaccountname", 
                            auth=auth)

import os 

# tenant id to draw error
tenant_id = "randomtenantid"
client_id = os.environ["purviewautomation-sp-client-id"]
client_secret = os.environ["purviewautomation-sp-secret"]
purview_account_name = os.environ["purview-account-name"]

def test_service_principal_set_access_token_error():
    # raise for status error
    auth = ServicePrincipalAuthentication(tenant_id, client_id, client_secret)


def test_az_identity_set_access_token_error():
    auth = AzIdentityAuthentication(credential=AzureCliCredential())






