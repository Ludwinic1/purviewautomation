from datetime import datetime

import requests


class ServicePrincipalAuthentication:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
        self.data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "resource": "https://purview.azure.net",
        }
        self.access_token = None
        self.access_token_expiration = datetime.now()

    def _set_access_token(self):
        access_token_request = requests.post(url=self.url, data=self.data)
        if access_token_request.status_code != 200:
            access_token_request.raise_for_status()

        self.access_token = access_token_request.json()["access_token"]
        self.access_token_expiration = datetime.fromtimestamp(int(access_token_request.json()["expires_on"]))

    def get_access_token(self):
        if self.access_token_expiration <= datetime.now():
            self._set_access_token()
        return self.access_token


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
