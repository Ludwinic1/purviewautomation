import random
import re
import string
from datetime import datetime, timedelta
from pprint import pprint as pretty_print
from typing import Dict, List, Optional, Tuple, Union

import requests

from .auth import AzIdentityAuthentication, ServicePrincipalAuthentication


class PurviewCollections:
    """Interact with Purview Collections.

    Attributes:
        purview_account_name: Name of the Purview account.
        auth: Access token automatically generated
                from the ServicePrincipalAuthentication class.
        header: Headers to be sent when calling the Purview APIs.
        collections_endpoint: The endpoint when calling collection APIs.
        collections_api_version: API version for the collection APIs.
        catalog_endpoint: The endpoint when calling the catalog APIs.
        catalog_api_version: API version for the catalog APIs.

    Returns:
        PurviewCollections object
    """

    def __init__(
        self, purview_account_name: str, auth: Union[ServicePrincipalAuthentication, AzIdentityAuthentication]
    ) -> None:
        self.purview_account_name = purview_account_name
        self.auth = auth.get_access_token()
        self.header = {"Authorization": f"Bearer {self.auth}", "Content-Type": "application/json"}
        self.collections_endpoint = f"https://{self.purview_account_name}.purview.azure.com/account/collections"
        self.collections_api_version = "2019-11-01-preview"
        self.catalog_endpoint = f"https://{self.purview_account_name}.purview.azure.com/catalog"
        self.catalog_api_version = "2022-03-01-preview"

    def list_collections(self, only_names: bool = False, pprint: bool = False, api_version: Optional[str] = None):
        """Returns the Purview collections.

        Args:
            only_names: If True, will return only the actual, friendly,
                and parent collection names.
            pprint: If True, will pretty print the collections.
                If only_names is also True, will pretty print only
                    the names listed in only_names.
            api_version: If None, default is "2019-11-01-preview".

        Returns:
            List of dictionaries containing the collection info.
                If only_names is True, will return a dictionary
                    of only_names items.
                If pprint is True, will print the values to the screen
                    and nothing is returned.
        """
        if not api_version:
            api_version = self.collections_api_version

        url = f"{self.collections_endpoint}?api-version={api_version}"
        collection_request = requests.get(url=url, headers=self.header)
        if collection_request.status_code != 200:
            if collection_request.status_code == 403:
                err_msg = (
                    "Not authorized. The Service Principal or user would need to be added as a Collection Admin on at "
                    "least one collection. For more info see: "
                    "https://learn.microsoft.com/en-us/azure/purview/catalog-permissions"
                )
                raise ValueError(err_msg)
            else:
                collection_request.raise_for_status()

        collections = collection_request.json()["value"]

        if only_names:
            coll_dict = {}
            for coll in collections:
                if "parentCollection" not in coll:
                    coll_dict[coll["name"]] = {"friendlyName": coll["friendlyName"], "parentCollection": None}
                else:
                    coll_dict[coll["name"]] = {
                        "friendlyName": coll["friendlyName"],
                        "parentCollection": coll["parentCollection"]["referenceName"],
                    }
            if pprint:
                pretty_print(coll_dict, sort_dicts=False)

            return coll_dict

        if pprint:
            pretty_print(collections, sort_dicts=False)

        return collections

    def get_real_collection_name(
        self, collection_name: str, api_version: Optional[str] = None, force_actual_name: bool = False
    ) -> str:
        """Returns the actual under the hood collection name.

        Args:
            collection_name: Name to check.
            api_version: If None, default is "2019-11-01-preview".
            force_actual_name: Edge case. If True, will check if the
                actual name is the name passed in. Useful if there
                are multiple friendly names.

        Returns:
            The actual name of the collection.

        Raises:
            If the collection doesn't exist, will raise an error
                that no collection exists.
            If multiple friendly names exist, will raise an error
                listing the multiple friendly names.
        """
        if not api_version:
            api_version = self.collections_api_version

        collections = self.list_collections(only_names=True, api_version=api_version)
        friendly_names = [
            (name, collections[name]) for name, value in collections.items() if collection_name == value["friendlyName"]
        ]

        if collection_name not in collections and len(friendly_names) == 0:
            err_msg = (
                "collection_name parameter value error. "
                f"The collection '{collection_name}' either doesn't exist or your don't have permission to start on it. "
                "If you're trying to create a child collection, would need to be a collection admin on that collection "
                "if it exists. Name is case sensitive."
            )
            raise ValueError(err_msg)
        elif collection_name not in collections and len(friendly_names) == 1:
            return friendly_names[0][0]
        elif collection_name in collections and len(friendly_names) <= 1:
            return collection_name

        if force_actual_name:
            for i in range(len(friendly_names)):
                if friendly_names[i][0] == collection_name:
                    return collection_name
        else:
            multiple_friendly_names = []
            for item in friendly_names:
                parent_name = item[1]["parentCollection"]
                parent_friendly_name = collections[parent_name]["friendlyName"]
                friendly_output = f"{item[0]}: [collection info: actual_name: {item[0]}, friendlyName: {item[1]['friendlyName']}, parentCollection: {parent_friendly_name}]"
                multiple_friendly_names.append(friendly_output)
            newline = "\n"
            err_msg = (
                f"Multiple collections exist with the friendly name '{collection_name}'. "
                f"Please choose and re-enter the first item from one of the options below in place of '{collection_name}': "
                f"{newline}{newline.join(map(str, multiple_friendly_names))} {newline}"
                f"If you want to use the collection name '{collection_name}' and it's listed as an option above as "
                f"a first item (actual_name), add the force_actual_name parameter to True. "
                "Ex: force_actual_name=True"
            )
            raise ValueError(err_msg)

    def _return_request_info(
        self, name: str, friendly_name: str, parent_collection: str, api_version: Optional[str] = None
    ) -> requests.request:
        """
        Internal helper function. Do not call directly.
        """
        if not api_version:
            api_version = self.collections_api_version

        url = f"{self.collections_endpoint}/{name}?api-version={api_version}"
        data = f'{{"parentCollection": {{"referenceName": "{parent_collection}"}}, "friendlyName": "{friendly_name}"}}'
        request = requests.put(url=url, headers=self.header, data=data)
        return request

    def _return_friendly_collection_names(
        self, collection_name: str, api_version: str
    ) -> List[Tuple[str, Dict[str, str]]]:
        """
        Internal helper function. Do not call directly.
        """
        collections = self.list_collections(only_names=True, api_version=api_version)
        friendly_names = [
            (name, collections[name]) for name, value in collections.items() if collection_name == value["friendlyName"]
        ]
        return friendly_names

    def _verify_collection_name(self, collection_name: str, uniqueness_retries: Optional[int] = 5) -> str:
        """Checks if the collection_name meets the Purview naming requirements.

        Args:
            collection_name: Name to check.
            uniqueness_retries: The number of attempts to make for creating a unique name.
                                Unlikely to happen even once, but exists for handling edgecases.

        Returns:
            The original collection_name or a random six character
                lowercase string if requirements are not met.
        """
        print(collection_name)
        pattern = "[a-zA-Z0-9]+"
        collection_check_pattern = re.search(pattern, collection_name)
        if collection_check_pattern:
            # returns the name the pattern matched.
            collection_name_check = collection_check_pattern.group()
            if len(collection_name) < 3 or len(collection_name) > 36 or (collection_name_check != collection_name):
                collection_name = "".join(random.choices(string.ascii_lowercase, k=6))
        else:
            collection_name = "".join(random.choices(string.ascii_lowercase, k=6))
        # Check if collection_name already in use, generate new if so
        i = 0
        existing_collection_names = self.list_collections(only_names=True).keys()
        while collection_name in existing_collection_names and i < uniqueness_retries:
            i += 1
            collection_name = "".join(random.choices(string.ascii_lowercase, k=6))
        if i == uniqueness_retries:
            raise SystemError(f"Did not create unique name within {uniqueness_retries} attempts. Aborting.")
        print(collection_name)
        print("===")
        return collection_name

    def _return_updated_collection_name(
        self,
        name: str,
        collection_dict: Dict[str, Dict[str, str]],
        parent_collection: str,
        friendly_names: List[str],
        api_version: str,
    ) -> str:
        """Internal helper function. Do not call directly.

        Returns one of the following:
        -Actual name if the collection exists in Purview and
            the parent collection names match.
        -If the name doesn't exist but meets the Purview naming
            requirements, returns the name.
        -If none of the above are returned, returns a random
            six character lowercase string.
        """
        if name in collection_dict and collection_dict[name]["parentCollection"] == parent_collection.lower():
            return name
        elif name in friendly_names:
            friendly_list = self._return_friendly_collection_names(name, api_version)

            if len(friendly_list) == 1 and friendly_list[0][1]["parentCollection"] == parent_collection.lower():
                name = friendly_list[0][0]
            elif len(friendly_list) == 1 and name in collection_dict:
                name = "".join(random.choices(string.ascii_lowercase, k=6))

            elif len(friendly_list) > 1:
                for collection in friendly_list:
                    found_name = ""
                    if collection[1]["parentCollection"] == parent_collection.lower():
                        found_name = collection[0]
                        break
                if found_name != "":
                    name = found_name
                else:
                    name = self._verify_collection_name(name)

            else:
                name = self._verify_collection_name(name)
        else:
            name = self._verify_collection_name(name)
        return name

    def _return_updated_collection_list(
        self,
        start_collection: str,
        collection_list: List[str],
        collection_dict: Dict[str, Dict],  # Need to check this
        api_version: str,
    ) -> List[str]:
        """Internal method. Do not call directly.

        Returns a collection list with the collection names
            used to call other methods.
        """
        updated_list = []
        friendly_names = [v["friendlyName"] for v in collection_dict.values()]
        for index, name in enumerate(collection_list):
            if index == 0:
                name = self._return_updated_collection_name(
                    name, collection_dict, start_collection, friendly_names, api_version
                )
            else:
                name = self._return_updated_collection_name(
                    name, collection_dict, updated_list[index - 1], friendly_names, api_version
                )
            updated_list.append(name)
        return updated_list

    def create_collections(
        self,
        start_collection: str,
        collection_names: Union[str, List[str]],
        force_actual_name: bool = False,
        api_version: Optional[str] = None,
        **kwargs,
    ) -> None:  # TODO Need to update this
        """Create collections.

        Can create any of the following:
        -One collection
        -Multiple Collections
        -One collection hierarchy (multiple parent/child relationships)
        -Multiple collection hierarchies

        Args:
            start_collection: Existing collection name.
                Use list_collections(only_names, pprint=True) to see
                all of the collection names. Accepts friendly and
                actual names.
            collection_names: collection name or names.
            force_actual_name: Edge Case. If multiple duplicate friendly names
                and one of the actual names is the name passed in.
            api_version: If None, default is "2019-11-01-preview".
            **kwargs:
                safe_delete_friendly_name: Used during the safe delete
                functionality. Don't call directly.

        Returns:
            Prints the successfully created collection/collections.
                If the collection/collections already exist, nothing prints.
        """
        if not api_version:
            api_version = self.collections_api_version

        coll_dict = self.list_collections(only_names=True, api_version=api_version)
        start_collection = self.get_real_collection_name(start_collection, api_version, force_actual_name)

        collection_list = []
        if not isinstance(collection_names, (str, list)):
            err = """The collection_names parameter has
                     to be a string or list type.
                  """
            raise ValueError(err)
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        collection_names_list = [[name] for name in collection_names]
        for item in collection_names_list:
            for name in item:
                if "/" in name:
                    names = name.split("/")
                    names = [name.strip() for name in names]
                    collection_list.append(names)
                else:
                    names = [name.strip() for name in item]
                    collection_list.append(names)

        for colls in collection_list:
            updated_collection_list = self._return_updated_collection_list(
                start_collection, colls, coll_dict, api_version
            )
            for index, name in enumerate(updated_collection_list):
                if index == 0:
                    if name in coll_dict and coll_dict[name]["parentCollection"].lower() == start_collection.lower():
                        continue
                    else:
                        if "safe_delete_friendly_name" in kwargs:
                            friendly_name = kwargs["safe_delete_friendly_name"]
                        else:
                            friendly_name = colls[index]
                    try:
                        request = self._return_request_info(
                            name=name,
                            friendly_name=friendly_name,
                            parent_collection=start_collection,
                            api_version=api_version,
                        )
                        print(request.content)
                        print("\n")
                    except Exception as e:
                        raise e

                else:
                    if (
                        name in coll_dict
                        and coll_dict[name]["parentCollection"].lower() == updated_collection_list[index - 1].lower()
                    ):
                        continue
                    else:
                        friendly_name = colls[index]
                        parent_collection = updated_collection_list[index - 1]
                    try:
                        request = self._return_request_info(
                            name=name,
                            friendly_name=friendly_name,
                            parent_collection=parent_collection,
                            api_version=api_version,
                        )
                        print(request.content)
                        print("\n")
                    except Exception as e:
                        raise e

    # Delete collections/assets

    def _safe_delete(self, collection_names: List[str], safe_delete_name: str) -> str:
        """Helper function. Do not run directly."""

        collections = self.list_collections(only_names=True)

        create_colls_list = []
        for name in collection_names:
            if len(collection_names) == 1:
                collection_name = self.get_real_collection_name(name)
                parent_name = collections[collection_name]["parentCollection"]
                friendly_name = collections[collection_name]["friendlyName"]
                create_collection_string = (
                    f"{safe_delete_name}"
                    f".create_collections(start_collection='{parent_name}', "
                    f"collection_names='{collection_name}', "
                    f"safe_delete_friendly_name='{friendly_name}')"
                )

            else:
                collection_name = self.get_real_collection_name(name)
                parent_name = collections[collection_name]["parentCollection"]
                friendly_name = collections[collection_name]["friendlyName"]
                create_collection_string = (
                    f"create_collections(start_collection='{parent_name}', "
                    f"collection_names='{collection_name}', "
                    f"safe_delete_friendly_name='{friendly_name}')"
                )
                create_colls_list.append(create_collection_string)

        print("Copy and run the below code in your program to recreate the collection/collections:", "\n")
        if len(collection_names) == 1:
            print(create_collection_string)
            print("\n")

        else:
            for item in create_colls_list:
                create_coll_final_string = f"{safe_delete_name}.{item}"
                print(create_coll_final_string)
                print("\n")

        print("end of code")
        print("\n")
        if len(create_colls_list) >= 1:
            return create_colls_list
        else:
            return create_collection_string

    def get_child_collection_names(self, collection_name: str, api_version: Optional[str] = None):
        if not api_version:
            api_version = self.collections_api_version

        url = f"{self.collections_endpoint}/{collection_name}/getChildCollectionNames?api-version={api_version}"
        try:
            get_collections_request = requests.get(url=url, headers=self.header)
        except Exception as e:
            raise e
        return get_collections_request.json()

    def delete_collection_assets(
        self,
        collection_names: Union[str, List[str]],
        timeout: int = 30,
        force_actual_name: bool = False,
        api_version: Optional[str] = None,
    ) -> None:
        """Delete all assets in one or multiple collections.

        Args:
            collection_names: Collection name or names to delete assets.
            timeout: How long in minutes before the code times out.
                Default is 30 minutes.
            force_actual_name: Edge Case. If multiple duplicate friendly names
                and one of the actual names is the name passed in.
            api_version: Catalog API version.
                If None, default is "2022-03-01-preview".

        Returns:
            Prints that the collection assets have been deleted.
        """
        if not api_version:
            api_version = self.catalog_api_version

        if not isinstance(collection_names, (str, list)):
            err = "The collection_names parameter has to be a string or list type."
            raise ValueError(err)
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        collections = self.list_collections(only_names=True)

        for name in collection_names:
            collection = self.get_real_collection_name(collection_name=name, force_actual_name=force_actual_name)

            future_timeout_time = datetime.now() + timedelta(minutes=timeout)
            final = False
            print(f"Attempting to delete assets in collection: '{collections[collection]['friendlyName']}'")
            print("Note: This could take time if there's a large number of assets in the collection")

            while not final and datetime.now() <= future_timeout_time:
                url = f"{self.catalog_endpoint}/api/search/query?api-version={api_version}"
                # max value is 1000
                data = f'{{"keywords": null, "limit": 1000, "filter": {{"collectionId": "{collection}"}}}}'
                asset_request = requests.post(url=url, data=data, headers=self.header)

                if asset_request.status_code == 403:
                    err_msg = (
                        f"The Service Principal or user needs to be listed as a Data Curator on collection '{collections[collection]['friendlyName']}' "
                        "in order to delete assets on that collection."
                    )
                    raise ValueError(err_msg)

                results = asset_request.json()
                total = len(results["value"])
                if total == 0:
                    final = True
                    print(
                        f"All assets have been successfully deleted from collection: '{collections[collection]['friendlyName']}'"
                    )
                    print("\n")
                else:
                    guids = [item["id"] for item in results["value"]]
                    guid_str = "&guid=".join(guids)
                    url = f"{self.catalog_endpoint}/api/atlas/v2/entity/bulk?guid={guid_str}"
                    delete_request = requests.delete(url, headers=self.header)

    def delete_collections(
        self,
        collection_names: Union[str, list],
        safe_delete: Optional[str] = None,
        delete_assets: bool = False,
        delete_assets_timeout: int = 30,
        force_actual_name: bool = False,
        api_version: Optional[str] = None,
    ) -> None:
        """Delete one or more collections.

            Pass in either the actual or friendly collection name.
            Can't pass in collections that have chidren.
            Use delete_collection_recursively instead.

        Args:
            collection_names: Collections to be deleted.
            safe_delete: The client name to be used when printing the safe delete commands.
            delete_assets: if True, will delete all of the assets from the collection.
            delete_assets_timeout: If delete_assets is True, this is the timeout for deleting the assets.
                If None, the default is 30 minutes.
            force_actual_name: Edge Case. If multiple duplicate friendly names
                and one of the actual names is the name passed in.
            api_version: If None, default is "2019-11-01-preview".

        Returns:
            Ouptuts to the screen the collection has been deleted.
        """
        if not api_version:
            api_version = self.collections_api_version

        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        if safe_delete:
            self._safe_delete(collection_names=collection_names, safe_delete_name=safe_delete)

        for name in collection_names:
            coll_name = self.get_real_collection_name(collection_name=name, force_actual_name=force_actual_name)
            child_collections_check = self.get_child_collection_names(coll_name)
            if child_collections_check["count"] > 0:
                err_msg = (
                    f"The collection '{name}' has child collections. Can only delete collections that have no children. "
                    "To delete collections and all of their children recursively, "
                    f"use: delete_collections_recursively('{name}')"
                )
                raise ValueError(err_msg)

            url = f"{self.collections_endpoint}/{coll_name}?api-version={api_version}"
            try:
                colls = self.list_collections(only_names=True)
                friendly_name = colls[coll_name]["friendlyName"]
                if delete_assets:
                    self.delete_collection_assets(collection_names=coll_name, timeout=delete_assets_timeout)
                delete_collections_request = requests.delete(url=url, headers=self.header)
                if not delete_collections_request.content:
                    print(f"The collection '{friendly_name}' was successfully deleted")
                    print("\n")
                else:
                    print(delete_collections_request.content)
            except Exception as e:
                raise e

    def _recursive_append(self, name: str, append_list: List[Union[str, None]]):
        """Internal method. Do not call directly."""

        child_collections = self.get_child_collection_names(name)
        if child_collections["count"] == 0:
            append_list.append(None)
        elif child_collections["count"] == 1:
            append_list.append(child_collections["value"][0]["name"])
        elif child_collections["count"] > 1:
            for v in child_collections.values():
                if isinstance(v, list):
                    for index, name in enumerate(v):
                        append_list.append(v[index]["name"])

    def _safe_delete_recursivly(
        self,
        delete_list: List[str],
        safe_delete_name: str,
        parent_name: str,
        also_delete_first_collection: bool = False,
    ) -> List[str]:
        initial_list = []
        clean_list = []

        collections = self.list_collections(only_names=True)
        print("Copy and run the below code in your program to recreate the", end=" ")
        print("collections and collection hierarchies:")
        print("\n")

        for index, name in enumerate(delete_list):
            if index == 0 or collections[name]["parentCollection"].lower() == parent_name.lower():
                first_string = f"{safe_delete_name}.create_collections(start_collection='{parent_name}', collection_names='{name}', safe_delete_friendly_name='{collections[name]['friendlyName']}')"
                initial_list.append(first_string)

            child_test = self.get_child_collection_names(name)
            if child_test["count"] == 1:
                initial_list.append(
                    f"{safe_delete_name}.create_collections(start_collection='{name}', collection_names='{child_test['value'][0]['name']}', safe_delete_friendly_name='{child_test['value'][0]['friendlyName']}')"
                )

            elif child_test["count"] > 1:
                for index, name2 in enumerate(child_test["value"]):
                    initial_list.append(
                        f"{safe_delete_name}.create_collections(start_collection='{name}', collection_names='{name2['name']}', safe_delete_friendly_name='{name2['friendlyName']}')"
                    )

        default_set = set()
        for item in initial_list:
            if item not in default_set:
                default_set.add(item)
                clean_list.append(item)
        if also_delete_first_collection:
            print(
                f"{safe_delete_name}.create_collections(start_collection='{collections[parent_name]['parentCollection']}', collection_names='{parent_name}', safe_delete_friendly_name='{collections[parent_name]['friendlyName']}')"
            )
        for item in clean_list:
            print(item)

        print("\n")
        print("end code", "\n")
        return clean_list

    def delete_collections_recursively(
        self,
        collection_names: Union[str, List[str]],
        safe_delete: Optional[str] = None,
        also_delete_first_collection: bool = False,
        delete_assets: bool = False,
        delete_assets_timeout: int = 30,
        force_actual_name: bool = False,
        api_version: Optional[str] = None,
    ) -> None:  # TODO need to update this and add force_actual_name
        """Delete one or multiple collection hierarchies.

        Args:
            collection_names: One or multiple names.
            safe_delete: Client name to be used when printing
                the safe delete commands.
            also_delete_first_collection: Deletes the start collection
                along with the children collections.
            force_actual_name: Edge Case. If multiple duplicate
                friendly names and one of the actual names is the
                    name passed in.
            delete_assets: if True, will delete all assets from every
                collection in the hierarchy.
            delete_assets_timeout: If delete_assets is True,
                this is the timeout for deleting the assets.
                If None, the default is 30 minutes.
            api_version: If None, default is "2019-11-01-preview".

        Returns:
            None. Will print out the collections being deleted.
        """
        if not api_version:
            api_version = self.collections_api_version

        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        for name in collection_names:
            delete_list = []
            recursive_list = []
            coll_name = self.get_real_collection_name(name, force_actual_name=force_actual_name)
            child_collections_check = self.get_child_collection_names(coll_name)
            if child_collections_check["count"] == 0:
                err_msg = (
                    f"The collection '{name}' has no child collections. Can only delete collections that have children. "
                    "To delete collections with no children, "
                    f"use: delete_collections('{name}')"
                )
                raise ValueError(err_msg)

            self._recursive_append(coll_name, delete_list)
            if delete_list[0] is not None:
                for item in delete_list:
                    self._recursive_append(item, recursive_list)
                for item2 in recursive_list:
                    if item2 is not None:
                        delete_list.append(item2)
                        self._recursive_append(item2, recursive_list)

            if safe_delete:
                if also_delete_first_collection:
                    self._safe_delete_recursivly(delete_list, safe_delete, coll_name, True)
                else:
                    self._safe_delete_recursivly(delete_list, safe_delete, coll_name)

            if delete_list[0] is not None:
                if also_delete_first_collection:
                    delete_list.insert(0, collection_names[0])
                for coll in delete_list[::-1]:  # starting from the most child collection
                    if delete_assets:
                        remove_duplicate_names = []
                        if coll not in remove_duplicate_names:
                            remove_duplicate_names.append(coll)
                        for coll in remove_duplicate_names:
                            self.delete_collection_assets(collection_names=coll, timeout=delete_assets_timeout)
                    self.delete_collections([coll])

    def extract_collections(
        self, start_collection_name: str, safe_delete_name: str = "client", api_version: Optional[str] = None
    ) -> None:
        """Extract and outputs the collection hierarchy structure.

        Args:
            start_collection_name: Collection to start on.
            safe_delete_name:  The client name to be used when printing
                the safe delete commands. Default is 'client'.
            api_version: API version to use. If None, default is "2019-11-01-preview".

        Returns:
            None. Will print out the script to create the collection hierarchy structure
            starting at the start_collection_name.
        """
        if not api_version:
            api_version = self.collections_api_version

        collections_list = []
        recursive_list = []

        start_collection_name = [start_collection_name]
        for name in start_collection_name:
            name = self.get_real_collection_name(name)
            self._recursive_append(name, collections_list)
            if collections_list[0] is not None:
                for item in collections_list:
                    self._recursive_append(item, recursive_list)
                for item2 in recursive_list:
                    if item2 is not None:
                        collections_list.append(item2)
                        self._recursive_append(item2, recursive_list)

        self._safe_delete_recursivly(collections_list, safe_delete_name, name, True)
