import json
import random
import string
from pprint import pprint
from typing import Optional, Union

import requests

from .auth import AzIdentityAuthentication, ServicePrincipalAuthentication
from .collections import PurviewCollections


class PurviewScanning(PurviewCollections):
    """Purview scanning class"""

    def __init__(
        self, purview_account_name: str, auth: Union[ServicePrincipalAuthentication, AzIdentityAuthentication]
    ) -> None:
        self.purview_account_name = purview_account_name
        self.auth = auth.get_access_token()
        self.auth_object = auth
        self.header = {"Authorization": f"Bearer {self.auth}", "Content-Type": "application/json"}
        self.data_sources_endpoint = f"https://{self.purview_account_name}.purview.azure.com/scan/datasources"
        self.data_sources_api_version = "2022-02-01-preview"

        # Initializing the PurviewCollections class
        super().__init__(purview_account_name=purview_account_name, auth=auth)

    # Helper methods
    def get_storage_info(self, name: str, subscription_id: str, resource_group_name: str):
        """Get Data Lake Info"""

        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{name}?api-version=2022-09-01"
        access_token = self.auth_object.get_access_token(scope="https://management.azure.com/.default")
        header = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.get(url, headers=header)

        if response.status_code != 200:
            response.raise_for_status()

        result = response.json()
        resource_id = result["id"]
        dfs_endpoint = result["properties"]["primaryEndpoints"]["dfs"]
        location = result["location"]

        return resource_id, dfs_endpoint, location

    def register_data_source(
        self,
        data_lake_name: str,
        subscription_id: str,
        resource_group_name: str,
        collection_name: str,
        nickname: Optional[str] = None,
    ) -> None:
        """Register a data source in Purview"""

        resource_id, dfs_endpoint, location = self.get_storage_info(
            data_lake_name, subscription_id, resource_group_name
        )
        url = f"{self.data_sources_endpoint}/{data_lake_name}?api-version={self.data_sources_api_version}"

        if not nickname:
            nickname = data_lake_name + "-" + "".join(random.choice(string.ascii_lowercase) for _ in range(4))

        data = {
            "kind": "AdlsGen2",
            "name": nickname,
            "properties": {
                "endpoint": dfs_endpoint,
                "subscriptionId": subscription_id,
                "resourceGroup": resource_group_name,
                "location": location,
                "resourceName": data_lake_name,
                "resourceId": resource_id,
                "collection": {
                    "type": "CollectionReference",
                    "referenceName": super().get_real_collection_name(collection_name),
                },
                # super() is calling the PurviewCollections class
            },
        }
        response = requests.put(url, headers=self.header, data=json.dumps(data))

        if response.status_code != 200:
            response.raise_for_status()

        print(f"Data source {data_lake_name} registered successfully in Purview!")
        return response.json()
