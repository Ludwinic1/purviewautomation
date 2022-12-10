[![Tests](https://github.com/Ludwinic1/purviewautomation/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Ludwinic1/purviewautomation/actions?query=branch%3Amain+workflow%3ATests)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/Ludwinic1/purviewautomation.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/Ludwinic1/purviewautomation)
[![pypi](https://img.shields.io/pypi/pyversions/purviewautomation)](https://pypi.org/project/purviewautomation/)
[![pypi version](https://img.shields.io/pypi/v/purviewautomation?color=blue)](https://pypi.org/project/purviewautomation/)
[![license](https://img.shields.io/github/license/Ludwinic1/purviewautomation)](https://github.com/Ludwinic1/purviewautomation/blob/main/LICENSE)

Welcome to Purview Automation!

Purview Automation is a Python wrapper library built on top of Azure Purview REST APIs that's designed to be simple to use and make scaling and automating Purview easier.

**Phase I is all about making it easier to work with, scale, rollback and automate Purview collections!**

---

**Documentation:** [https://purviewautomation.netlify.app](https://purviewautomation.netlify.app)

**Source Code:** [https://github.com/Ludwinic1/purviewautomation](https://github.com/Ludwinic1/purviewautomation)

---


Key benefits:

- **Easy**: Create and delete collections and collection hierarchies with one line of code
- **Rollback**: Rollback to previous collection hierarchy states and save versions for later use
- **Deploy**: Extract/deploy collections to UAT/PROD environments to ensure consistency across Purviews 
- **Delete Assets**: Delete all assets in a collection or all assets in a collection hierarchy 
- **Safe**: Does **NOT** supercede any Purview permissions. Unable to create/delete collections unless the Collection Admin role is granted in Purview. See: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions).
  
 
- **Ease of Use**: Use either the friendly collection name (what is shown in the Purview UI) or the actual collection name (under the hood name) instead of being required to find and use the actual name when calling APIs. See: [Purview Collection Names Overview](https://purviewautomation.netlify.app/how-purview-names-work/)

---

**Example Showcase:**

Azure Purview before:

![Purview Before](https://purviewautomation.netlify.app/img/readme/image01.png)


<!-- ![Purview Before](https://github.com/Ludwinic1/purviewautomation/blob/main/docs/img/readme/image01.png) -->

Write simple code:

```Python
client.create_collections(start_collection="My-Collection",
                          collection_names="Sub Collection 1/Deeper Sub 1/Deeper Sub 2/Deeper Sub 3")
```

Azure Purview after:

![Purview After](https://purviewautomation.netlify.app/img/readme/image02.png)

<!-- ![Purview After](https://github.com/Ludwinic1/purviewautomation/blob/main/docs/img/readme/image02.png) -->

---

## **Installation**
```Python
pip install purviewautomation
```

## **Quick Start**

### **Connect to Purview With a Service Principal**

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

**Important:**
    Make sure the Service Principal is assigned the **Collection Admin** role to a collection in Purview. The below examples assume the Service Principal is assigned the Collection Admin role at the root collection level. See here for more info: [Assign the Service Principal the Collection Admin Role in Purview](https://purviewautomation.netlify.app/create-a-service-principal/#how-to-assign-the-service-principal-the-collection-admin-role-in-purview). 
    
To learn how to create a Service Principal, see: [Create a Service Principal](https://purviewautomation.netlify.app/create-a-service-principal/#how-to-create-a-service-principal).

<br>

### **Connect to Purview With the Azure-Identity Package Via the Azure CLI**

Alternatively, to connect with your own credentials or other options (Managed Identity, Environment Credentials, Azure CLI Credentials) instead of the Service Principal, use the Azure-Identity package:

```pip install azure-identity```

Then sign in with your Azure CLI credentials (in a terminal type `az login` and sign in via the link that pops up):

```Python
from azure.identity import AzureCliCredential

from purviewautomation import PurviewCollections, AzIdentityAuthentication

auth = AzIdentityAuthentication(credential=AzureCliCredential())

client = PurviewCollections(purview_account_name="yourpurviewaccountname", 
                            auth=auth)
```                            
**Important:**
    Make sure the user or entity is assigned the **Collection Admin** role to a collection in Purview. The below examples assume the role is assigned at the root collection level (yourpurviewaccountname collection). For more info, see: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions).

<br>

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

## **Delete All Assets in a Collection**
**Important:**
    The Service Principal or user that authenticated/connected to Purview would need to be assigned the **Data Curator** role on the collection in order to delete assets in that collection. For more info, see: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions)

```Python
client.delete_collection_assets(collection_names="My First Collection")
```

## **Delete All Assets in Multiple Collections**
**Important:**
    The Service Principal or user that authenticated/connected to Purview would need to be assigned the **Data Curator** role on the collection in order to delete assets in that collection. For more info, see: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions)

```Python
collections = ["Random Collection", "hierarchy sub2"]
client.delete_collection_assets(collection_names=collections)
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

## **Delete a Collection with Rollback Enabled**
```Python
# Will delete the collection 
# and output the exact script needed to recreate the collection

client.delete_collections(collection_names="Random Collection 2", 
                          safe_delete="client")
```

## **Delete All Assets in a Collection and Delete the Collection**
**Important:**
    The Service Principal or user that authenticated/connected to Purview would need to be assigned the **Data Curator** role on the collection in order to delete assets in that collection. For more info, see: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions)

```Python
# Delete all of the assets in the collection 
# And delete the collection as well

client.delete_collections("My First Collection", delete_assets=True)
```

## **Delete a Collection Hierarchy with Rollback Enabled**
```Python
# Will delete all of the children and their children and output the exact script 
# needed to recreate the entire hierarchy to rollback or deploy to another Purview

client.delete_collections_reursively("My First Collection", safe_delete="client")
```

## **Delete All Assets in a Collection Hierarchy and Delete the Hierarchy**
**Important:**
    The Service Principal or user that authenticated/connected to Purview would need to be assigned the **Data Curator** role on the collection in order to delete assets in that collection. For more info, see: [Purview Roles](https://learn.microsoft.com/en-us/azure/purview/catalog-permissions)

```Python
# Delete all of the assets in all of the collections under the hierarchy 
# And delete the collection hierarchy as well

client.delete_collections_recursively("My First Collection", delete_assets=True)
```