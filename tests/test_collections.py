import os
from typing import Any, List, Tuple

import pytest
import requests

from purviewautomation import PurviewCollections, ServicePrincipalAuthentication

TENANT_ID = os.environ["purviewautomation-tenant-id"]
CLIENT_ID = os.environ["purviewautomation-sp-client-id"]
CLIENT_SECRET = os.environ["purviewautomation-sp-secret"]
PURVIEW_ACCOUNT_NAME = os.environ["purview-account-name"]

# Service Principal for Testing Insufficient Permissions
LESS_ACCESS_CLIENT_ID = os.environ["less-access-sp-client-id"]
LESS_ACCESS_CLIENT_SECRET = os.environ["less-access-sp-secret"]

auth = ServicePrincipalAuthentication(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)


# Helper function
def collection_check_helper(collection_names: str) -> Tuple[List[str], List[Any]]:
    names = [name.strip() for name in collection_names.split("/")]
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    return names, friendly_names


# List collections
def test_list_colls():
    collections = client.list_collections()
    assert isinstance(collections, list)


def test_list_colls_only_names():
    collections = client.list_collections(only_names=True)
    assert isinstance(collections, dict)


def test_list_colls_pprint():
    client.list_collections(pprint=True)


def test_list_colls_only_names_pprint():
    client.list_collections(only_names=True, pprint=True)


def test_list_colls_raise__permission_error():
    with pytest.raises(ValueError):
        auth = ServicePrincipalAuthentication(
            tenant_id=TENANT_ID, client_id=LESS_ACCESS_CLIENT_ID, client_secret=LESS_ACCESS_CLIENT_SECRET
        )
        client = PurviewCollections(purview_account_name=PURVIEW_ACCOUNT_NAME, auth=auth)
        client.list_collections(pprint=True)


# Create collections
def test_create_single_collection():
    # Change this to be dynamic to use purview account name
    client.create_collections(start_collection=PURVIEW_ACCOUNT_NAME, collection_names="My-Company")
    client.create_collections(start_collection="My-Company", collection_names="mytest1")
    name, friendly_names = collection_check_helper("mytest1")
    assert name[0] in friendly_names


def test_create_single_collection02():
    client.create_collections(start_collection="My-Company", collection_names=["my test 2"])
    name, friendly_names = collection_check_helper("my test 2")
    assert name[0] in friendly_names


def test_create_collections_multiple01():
    collection_names = "test1/test 2/ test 3/a/reallylongnameofacollectionstest"
    client.create_collections(start_collection="My-Company", collection_names=collection_names)
    names, friendly_names = collection_check_helper(collection_names=collection_names)
    for name in names:
        assert name in friendly_names


def test_create_collections_multiple02():
    collections_first = "coll1/coll2/coll 3/coll4/coll5/coll 6"
    collections_second = "newcoll1/newcoll 2/ new coll 3 / new coll4/ newcoll5/newcoll6"
    client.create_collections(start_collection="My-Company", collection_names=[collections_first, collections_second])
    first_names, friendly_names = collection_check_helper(collections_first)
    second_names, friendly_names = collection_check_helper(collections_second)
    for name, name2 in zip(first_names, second_names):
        assert name in friendly_names
        assert name2 in friendly_names


def test_create_collections_type_error():
    with pytest.raises(ValueError):
        collections = {"name1": "name2"}
        client.create_collections(start_collection="My-Company", collection_names=collections)


def test_create_collections_safe_delete_friendly_name():
    client.create_collections(
        start_collection="My-Company", collection_names="safe delete test", safe_delete_friendly_name="safe delete test"
    )
    name, friendly_names = collection_check_helper("safe delete test")
    assert name[0] in friendly_names


# Delete collections
def test_delete_collection():
    client.delete_collections("mytest1")
    client.delete_collections("my test 2", safe_delete="client")
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "mytest1" not in friendly_names
    assert "my test 2" not in friendly_names


def test_delete_multiple_collections():
    client.create_collections(
        start_collection=PURVIEW_ACCOUNT_NAME, collection_names=["multideletecoll1", "multideletecoll2"]
    )
    client.delete_collections(["multideletecoll1", "multideletecoll2"])
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "multideletecoll1" not in friendly_names
    assert "multideletecoll2" not in friendly_names


def test_delete_multiple_collections_safe_delete():
    client.create_collections(
        start_collection=PURVIEW_ACCOUNT_NAME, collection_names=["multideletecoll10", "multideletecoll11"]
    )
    client.delete_collections(["multideletecoll10", "multideletecoll11"], safe_delete="client")
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "multideletecoll10" not in friendly_names
    assert "multideletecoll11" not in friendly_names


def test_delete_collections_recursively():
    client.delete_collections_recursively("My-Company", safe_delete="client")
    my_company_real_name = client.get_real_collection_name("My-Company")
    child_collections = client.get_child_collection_names(my_company_real_name)
    assert child_collections["count"] == 0


def test_delete_collections_recursively02():
    client.create_collections(start_collection="My-Company", collection_names="test 1")
    client.delete_collections_recursively("My-Company", also_delete_first_collection=True)
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "My-Company" not in friendly_names


def test_delete_collection_and_assets():
    client.create_collections(start_collection=PURVIEW_ACCOUNT_NAME, collection_names="assets1")
    client.delete_collections(collection_names="assets1", delete_assets=True)
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "assets1" not in friendly_names


def test_delete_collections_child_error():
    with pytest.raises(ValueError):
        client.create_collections(PURVIEW_ACCOUNT_NAME, "childtest1/childtest2")
        client.delete_collections("childtest1")


def test_delete_collections_type_error():
    with pytest.raises(ValueError):
        incorrect_type = {"test1": "test2"}
        client.delete_collections(collection_names=incorrect_type)


# Get real collection name
def test_get_real_collection_name_error():
    with pytest.raises(ValueError):
        client.get_real_collection_name(collection_name="fake collection")


def test_force_actual_name():
    client.create_collections(start_collection=PURVIEW_ACCOUNT_NAME, collection_names=["Collection 1", "Collection 2"])
    # create duplicate collection name
    client.create_collections("Collection 1", "duplicatename")
    client.create_collections("Collection 2", "duplicatename")
    client.create_collections(start_collection="duplicatename", collection_names="test sub 1", force_actual_name=True)
    name, friendly_names = collection_check_helper("test sub 1")
    assert name[0] in friendly_names


def test_multiple_friendly_names():
    with pytest.raises(ValueError):
        client.create_collections(start_collection="duplicatename", collection_names="test2")


# Delete collection assets

# delete collection assets helper function
def delete_assets_helper(collection_name: str):
    actual_coll_name = client.get_real_collection_name(collection_name=collection_name)
    url = f"{client.catalog_endpoint}/api/search/query?api-version={client.catalog_api_version}"
    data = f'{{"keywords": null, "limit": 1000, "filter": {{"collectionId": "{actual_coll_name}"}}}}'
    asset_request = requests.post(url=url, data=data, headers=client.header)
    results = asset_request.json()
    total = len(results["value"])
    return total


def test_delete_collection_assets():
    client.delete_collection_assets(collection_names="Collection 2")
    total = delete_assets_helper("Collection 2")
    assert total == 0


def test_delete_collection_assets_recursively():
    client.create_collections(PURVIEW_ACCOUNT_NAME, collection_names="Delete Assets Collection")
    client.create_collections("Delete Assets Collection", collection_names="sub assets1/sub assets2/sub assets3")
    client.delete_collections_recursively("Delete Assets Collection", delete_assets=True)
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "sub assets1" not in friendly_names
    assert "sub assets2" not in friendly_names
    assert "sub assets3" not in friendly_names
    assert "Delete Assets Collection" in friendly_names


def test_delete_assets_raise_error():
    with pytest.raises(ValueError):
        collection = {"test1", "test2"}
        client.delete_collection_assets(collection_names=collection)


# Extract collections
def test_extract_collections():
    client.extract_collections(start_collection_name=PURVIEW_ACCOUNT_NAME, safe_delete_name="client")


# Safe delete
def test_safe_delete_recursively():
    client.create_collections(PURVIEW_ACCOUNT_NAME, "collection11")
    client.create_collections("collection11", "testa/testb/testc/testd")
    delete_list = ["testa", "testb", "testc", "testd"]
    parent_name = "collection11"
    safe_delete_list = client._safe_delete_recursivly(
        delete_list=delete_list, safe_delete_name="client", parent_name=parent_name
    )

    first_coll = "client.create_collections(start_collection='collection11', collection_names='testa', safe_delete_friendly_name='testa')"
    second_coll = "client.create_collections(start_collection='testa', collection_names='testb', safe_delete_friendly_name='testb')"
    third_coll = "client.create_collections(start_collection='testb', collection_names='testc', safe_delete_friendly_name='testc')"
    fourth_coll = "client.create_collections(start_collection='testc', collection_names='testd', safe_delete_friendly_name='testd')"

    assert safe_delete_list[0] == first_coll
    assert safe_delete_list[1] == second_coll
    assert safe_delete_list[2] == third_coll
    assert safe_delete_list[3] == fourth_coll


def test_safe_delete():
    safe_delete_string = client._safe_delete(collection_names=["testa"], safe_delete_name="client")
    coll_string = "client.create_collections(start_collection='collection11', collection_names='testa', safe_delete_friendly_name='testa')"
    assert safe_delete_string == coll_string


# Verify collection name


def test_verify_random_name():
    random_name = client._verify_collection_name("/")
    assert isinstance(random_name, str) and len(random_name) == 6
