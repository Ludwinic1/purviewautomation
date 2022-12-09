import os

import azure.identity
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


def test_az_identity_raise_error():
    with pytest.raies(azure.identity.CredentialUnavailableError):
        auth = AzIdentityAuthentication(credential=AzureCliCredential())
        client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)


