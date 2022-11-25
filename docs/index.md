Welcome to Purview Automation! 

Purview Automation is a Python wrapper library around Purview APIs that's designed to be simple to use and make scaling and automating Purview easier. 

**Phase I is all about making it easier to working with, scale, rollback and automate Purview collections!** 

Key benefits:

- **Easy**: Create, delete and list collections and collection hierarchies with one line of code
- **Rollback**: Rollback to previous collection hierarchy states and save versions for later use
- **Deploy**: Extract and deploy collections to upper environments (UAT/PROD) so the collection hierarchy structures are consistent across all Purviews 
- **Safe**: Does **NOT** supercede any Purview permissions. Unable to create/delete collections unless the Collection Admin role is granted in Purview. See: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions)
- **Delete Assets**: Delete assets in a collection or all assets in a collection hierarchy   
 
- **Ease of Use**: Use either the friendly collection name (what is shown in the Purview UI) or the actual collection name (under the hood name) instead of being required to find and use the actual collection name. See: [Purview Collection Names Overview](how-purview-names-work.md)
  

<br>
See this **5 minute video** on why this library was created, what problems it solves and how it can help you save time!  
<br>

**For a detailed step-by-step walkthrough and full reference guide, see: [Full Walkthrough Tutorial](./tutorial/first-steps.md)**


## **Installation**
```console
$ pip install purviewautomation

---> 100%
```

## **Quick Start**

Create a Python file `main.py` (can be called anything), gather the Azure Service Principal information and replace `yourtenantid`, `yourclientid`, `yourclientsecret` and `yourpurviewaccountname`:

```Python
from purviewautomation import (ServicePrincipalAuthentication, 
                                PurviewCollections)

auth = ServicePrincipalAuthentication(tenant_id="yourtenantid",
                                      client_id="yourclientid",
                                      client_secret="yourclientsecret")

client = PurviewCollections(purview_account_name="yourpurviewaccountname",
                            auth=auth)
```

!!! important
    Make sure the Service Principal is assigned the Collection Admin role to a collection in Purview. The below examples assume the Service Principal is assigned the Collection Admin role at the root collection level. See here for more info: [Create a Service Princpal and Assign the Collection Admin Role in Purview](create-a-service-principal.md) 


Now interact with the Purview collections:

## **Print Collections**
```Python
print(client.list_collections())
```

## **Print Only the Relevant Collection Name Info**
```Python
client.list_collections(only_names=True, pprint=True)
```

## **Return Collections as a List or Only Names as a Dictionary**
```Python
collection_list = client.list_collections()
for coll in collection_list:
    print(coll)

# Return only the relevant names as a dictionary
collection_names = client.list_collections(only_names=True)
for name, value in collection_names.items():
    print(name, value)

# Return just the keys (actual names)
for name in collection_names:
    print(name)

# Return the friendly names or parent collection names
for name in collection_names.values():
    friendly_name = name["friendlyName"]
    parent_name = name["parentCollection"] 
```


## **Create a Collection**
```Python
# Replace "yourpurviewaccountname"

client.create_collections(start_collection="yourpurviewaccountname",
                          collection_names="My First Collection")
```                        

## **Create a Collection Hierarchy**
```Python
# Create a collection hierarchy
 
client.create_collections(start_collection="My First Collection",
                          collection_names="Child1/Sub Collection 1/Deeper Sub Collection1")
```

## **Create Multiple Collections**
```Python
# Both random collections are at the same level under Sub Collection 1

client.create_collections(start_collection="Sub Collection 1", 
                          collection_names=["Random Collection", "Random Collection 2"])
```
## **Create Multiple Collection Hierarchies**
```Python
hierarchy_1 = "hierarchy1/hierarchysub1/hierarchysub2/hierarchysub3"
hierarchy_2 = "hierarchy 2/hierarchy sub2"
client.create_collections(start_collection="My First Collection",
                          collection_names=[hierarcy_1, hierarchy_2])
```    

## **Extract Collections**
```Python
# Useful for recreating entire collection hierarchies in a new Purview
# or saving the output as a version to rollback later
# Will output the exact script needed to recreate the entire hierarchy

client.extract_collections("My First Collection")
```

## **Delete a Collection**
```Python
client.delete_collections(collection_names="Random Collection")
```
## ** Delete a Collection with Rollback Enabled**
```Python
# Will delete the collection and output the exact script needed to recreate the collection

client.delete_collections(collection_names="Random Collection 2", 
                          safe_delete="client")
```                    
## ** Delete a Collection Hierarchy with Rollback Enabled**
```Python
# Will delete all of the children and their children and output the exact script 
# needed to recreate the entire hierarchy to rollback or deploy to another Purview

client.delete_collections_reursively("My First Collection", safe_delete="client")
```










