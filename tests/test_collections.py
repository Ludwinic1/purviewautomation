import os 
import random 
import string 
from purviewautomation import PurviewCollections, ServicePrincipalAuthentication

tenant_id = os.environ['purviewautomation-tenant-id']
client_id = os.environ['purviewautomation-sp-client-id']
client_secret = os.environ['purviewautomation-sp-secret']
# purview_account_name = os.environ['purview_account_name'] # to be used in github action input
# purview_account_name = ''.join(random.choices(string.ascii_lowercase, k=10)) # Use in github actions

# To use for PS to generate random 10 character string
# $L = [Char[]]'abcdefghijklmnopqrstuvwxyz'
# $Lower = (Get-Random -Count 10 -InputObject $L) -join ''

# PS to create Purview
#login azure
# get object ID of SPN in AAD and save it in secret. Along with SPN info. 
# New-AzResourceGroup -Name myResourceGroup -Location 'East US'
# New-AzPurviewAccount -Name yourPurviewAccountName -ResourceGroupName myResourceGroup -Location eastus -IdentityType SystemAssigned -SkuCapacity 4 -SkuName Standard -PublicNetworkAccess Enabled
# az purview account add-root-collection-admin --account-name [Microsoft Purview Account Name] --resource-group [Resource Group Name] --object-id [User Object Id]
# https://learn.microsoft.com/en-us/azure/purview/create-microsoft-purview-powershell?tabs=azure-powershell

auth = ServicePrincipalAuthentication(tenant_id, client_id, client_secret)

client = PurviewCollections('purview-test-2', auth=auth)

# Helper function
def collection_check_helper(collection_names: str) -> list[list]:
    names = [name.strip() for name in collection_names.split('/')]
    collections = client.list_collections(only_names=True)
    friendly_names = [coll['friendlyName'] for coll in collections.values()]
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
    client.create_collections(start_collection='purview-test-2', collection_names='My-Company') 
    client.create_collections(start_collection='My-Company', collection_names='mytest1')
    name, friendly_names = collection_check_helper('mytest1')
    assert name[0] in friendly_names


def test_create_single_collection02():
    client.create_collections(start_collection='My-Company', collection_names=['my test 2'])
    name, friendly_names = collection_check_helper('my test 2')
    assert name[0] in friendly_names


def test_create_collections_multiple01():
    collection_names = 'test1/test 2/ test 3/a/reallylongnameofacollectionstest'
    client.create_collections(start_collection='My-Company', 
                              collection_names=collection_names)
    names, friendly_names = collection_check_helper(collection_names=collection_names)
    for name in names:
        assert name in friendly_names


def test_create_collections_multiple02():
    collections_first = 'coll1/coll2/coll 3/coll4/coll5/coll 6'
    collections_second = 'newcoll1/newcoll 2/ new coll 3 / new coll4/ newcoll5/newcoll6'
    client.create_collections(start_collection='My-Company', 
                              collection_names=[collections_first, collections_second])
    first_names, friendly_names = collection_check_helper(collections_first)
    second_names, friendly_names = collection_check_helper(collections_second)
    for name, name2 in zip(first_names, second_names):
        assert name in friendly_names
        assert name2 in friendly_names

# Delete collections
def test_delete_collection():
    client.delete_collections('mytest1')
    client.delete_collections('my test 2')


def test_delete_collections_recursively():
    client.delete_collections_recursively('My-Company')
    real_name = client.get_real_collection_name('My-Company')
    child_collections = client.get_child_collection_names(real_name)
    assert child_collections['count'] == 0

def test_delete_collections_recursively02():
    client.create_collections(start_collection='My-Company', collection_names='test 1')
    client.delete_collections_recursively('My-Company', also_delete_first_collection=True)
    collections = client.list_collections(only_names=True)
    friendly_names = [coll['friendlyName'] for coll in collections.values()]
    assert 'My-Company' not in friendly_names


    

# client.delete_collections_recursively('My-Company', safe_delete='client')


# client.create_collections(start_collection='7bprpb', collection_names='test1', safe_delete_friendly_name='test1')
# client.create_collections(start_collection='test1', collection_names='khvqhd', safe_delete_friendly_name='test 2')
# client.create_collections(start_collection='7bprpb', collection_names='coll1', safe_delete_friendly_name='coll1')
# client.create_collections(start_collection='coll1', collection_names='coll2', safe_delete_friendly_name='coll2')
# client.create_collections(start_collection='7bprpb', collection_names='newcoll1', safe_delete_friendly_name='newcoll1')
# client.create_collections(start_collection='newcoll1', collection_names='uoblms', safe_delete_friendly_name='newcoll 2')
# client.create_collections(start_collection='khvqhd', collection_names='xxqlte', safe_delete_friendly_name='test 3')
# client.create_collections(start_collection='coll2', collection_names='niivlp', safe_delete_friendly_name='coll 3')
# client.create_collections(start_collection='uoblms', collection_names='wrgpkt', safe_delete_friendly_name='new coll 3')
# client.create_collections(start_collection='xxqlte', collection_names='olfzzn', safe_delete_friendly_name='a')
# client.create_collections(start_collection='niivlp', collection_names='coll4', safe_delete_friendly_name='coll4')
# client.create_collections(start_collection='wrgpkt', collection_names='aojqwi', safe_delete_friendly_name='new coll4')
# client.create_collections(start_collection='olfzzn', collection_names='reallylongnameofacollectionstest', safe_delete_friendly_name='reallylongnameofacollectionstest')
# client.create_collections(start_collection='coll4', collection_names='coll5', safe_delete_friendly_name='coll5')
# client.create_collections(start_collection='aojqwi', collection_names='newcoll5', safe_delete_friendly_name='newcoll5')
# client.create_collections(start_collection='coll5', collection_names='jijgqz', safe_delete_friendly_name='coll 6')
# client.create_collections(start_collection='newcoll5', collection_names='newcoll6', safe_delete_friendly_name='newcoll6')