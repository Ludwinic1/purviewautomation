[![Tests](https://github.com/Ludwinic1/purviewautomation/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Ludwinic1/purviewautomation/actions?query=branch%3Amain+workflow%3ATests)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/Ludwinic1/purviewautomation.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/Ludwinic1/purviewautomation)
[![license](https://img.shields.io/github/license/Ludwinic1/purviewautomation.svg)](https://github.com/Ludwinic1/purviewautomation/blob/main/LICENSE)

Welcome to Purview Automation!

Purview Automation is a Python wrapper library built on top of Purview REST APIs that's designed to be simple to use and make scaling and automating Purview easier.
<br>
<br>

Documentation: mydocumentation link

See this **5 minute video** on why this library was created, what problems it solves and how it can help you save time!  
<br>

**For a detailed step-by-step walkthrough and full reference guide, see: [Full Walkthrough](./tutorial/first-steps.md)**


## **Installation**
`pip install purviewautomation`

## **Quick Start**

Create a Python file `main.py` (can be called anything) and gather the Azure Service Principal information to use and replace the tenantid, clientid, client secret and Purview account name per below:

```Python
from purviewautomation import (ServicePrincipalAuthentication, 
                                PurviewCollections)

auth = ServicePrincipalAuthentication(tenantid="yourtenantid",
                                        clientid="yourclientid",
                                        clientsecret="yourclientsecret")

client = PurviewCollections(purview_account_name="yourpurviewaccountname",
                            auth=auth)

# Now interact and print the collections
print(client.list_collections())
```

## **Create a Collection**

```Python 
client.create_collections(start_collection="yourpurviewaccountname",
                          collection_names="My First Collection"
                        )
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

## **Extract Collections**
```Python
# Useful for recreating entire collection hierarchies in a new Purview
# or saving the output as a version to rollback later.
# Will output the exact script needed to recreate the entire hierarchy. 

client.extract_collections("My First Collection")
```

## **Delete a Collection**
```Python
client.delete_collections(collection_names="Random Collection")
```

## **Delete a Collection Hierarchy**
```Python 
# Will delete all of the children and their children under My First Collection
 
client.delete_collections_recursively("My First Collection")
```