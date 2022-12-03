import os
from typing import Any, List, Tuple

from purviewautomation import PurviewCollections, ServicePrincipalAuthentication

tenant_id = os.environ["purviewautomation-tenant-id"]
client_id = os.environ["purviewautomation-sp-client-id"]
client_secret = os.environ["purviewautomation-sp-secret"]
purview_account_name = os.environ["purview-account-name"]

auth = ServicePrincipalAuthentication(tenant_id, client_id, client_secret)
client = PurviewCollections(purview_account_name, auth=auth)


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


# Create collections
def test_create_single_collection():
    # Change this to be dynamic to use purview account name
    client.create_collections(start_collection=purview_account_name, collection_names="My-Company")
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


# Delete collections
def test_delete_collection():
    client.delete_collections("mytest1")
    client.delete_collections("my test 2")


def test_delete_collections_recursively():
    client.delete_collections_recursively("My-Company")
    real_name = client.get_real_collection_name("My-Company")
    child_collections = client.get_child_collection_names(real_name)
    assert child_collections["count"] == 0


def test_delete_collections_recursively02():
    client.create_collections(start_collection="My-Company", collection_names="test 1")
    client.delete_collections_recursively("My-Company", also_delete_first_collection=True)
    collections = client.list_collections(only_names=True)
    friendly_names = [coll["friendlyName"] for coll in collections.values()]
    assert "My-Company" not in friendly_names
