from datetime import datetime

from msal import ConfidentialClientApplication


# Base authentication
def _msal_get_access_token(tenant_id, client_id, client_secret, scope):
    app = ConfidentialClientApplication(
        client_id=client_id, client_credential=client_secret, authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    result = None
    result = app.acquire_token_silent(scopes=scope, account=None)

    if not result:
        result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise ValueError(result.get("error") + ": " + result.get("error_description"))


class ServicePrincipalAuthentication:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self, scope="https://purview.azure.net/.default"):
        access_token = _msal_get_access_token(
            tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self.client_secret, scope=[scope]
        )
        return access_token


class AzIdentityAuthentication:
    def __init__(self, credential):
        self.scope = "73c2949e-da2d-457a-9607-fcc665198967/.default"
        self.credential = credential
        self.access_token = None
        self.access_token_expiration = datetime.now()

    def _set_access_token(self):
        access_token_request = self.credential.get_token(self.scope)
        self.access_token = access_token_request.token
        self.access_token_expiration = datetime.fromtimestamp(access_token_request.expires_on)

    def get_access_token(self):
        if self.access_token_expiration <= datetime.now():
            self._set_access_token()
        return self.access_token
