import os

import pytest
import requests
from azure.identity import AzureCliCredential

from purviewautomation import (
    AzIdentityAuthentication,
    PurviewCollections,
    ServicePrincipalAuthentication,
)

PURVIEW_ACCOUNT_NAME = os.environ["purview-account-name"]


def test_service_principal_raise_error():
    with pytest.raises(requests.exceptions.HTTPError):
        auth = ServicePrincipalAuthentication(tenant_id="asldf", client_id="alsdjf", client_secret="alsdjf")
        client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)


def test_az_identity():
    auth = AzIdentityAuthentication(AzureCliCredential())
    client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)
    assert type(client) == PurviewCollections


def test_az_identity_raise_error():
    with pytest.raises(AttributeError):
        credential = "randomcredential"
        auth = AzIdentityAuthentication(credential=credential)
        client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)
