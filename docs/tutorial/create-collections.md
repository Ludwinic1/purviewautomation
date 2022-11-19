### Overview 

::: purviewautomation.collections.PurviewCollections.create_collections
    options:
        heading_level: 0

### Examples
The start_collection has to already exist in Purview. Pass in either the friendly name or the real name of the collection.

Code will automatically trim an leading or training whitespaces.
Collection names are case sensitive. My-Company and my-company are two different names.

# **Create One Collection**
If the Purview collections look like this:

![Collections](../img/tutorial/create-collections/image01.png)

** Example 1: Create one collection starting from any of the three listed (purview-test-2, My-Company, test 1):**
```Python
client.create_collections(start_collection="purview-test-2", collection_names="new collection 1")
```
This will create a collection under purview-test-2 (same level as the My-Company collection):
![Collections](../img/tutorial/create-collections/image02.png)

**Example 2: Create from `test 1`. As you can see, `sub test coll` is listed as a child of `test 1`. The keyword arguments can be ommited if desired:**
```Python
client.create_collections("test 1", "sub test coll")
```
![Collections](../img/tutorial/create-collections/image03.png)


# **Create Multiple Collections**
To create multiple collections, pass in a list to the collection_names parameter. The `subcoll1` and `subcoll2` collections would be children of `test 1`:
```Python
client.create_collections(start_collection="test 1", ["subcoll 1", "subcoll2"])
```
![Collections](../img/tutorial/create-collections/image04.png)

**Example 2: Create four collections under `subcoll 1`:**
```Python
colls = ["newcoll1", "newcoll2", "Random Collection", "Another Random Collection"]
client.create_collections("subcoll 1", colls)
```
![Collections](../img/tutorial/create-collections/image05.png)


# **Create One Collection Hierarcy**
To create a collection hierarchy, add `/` for parent/child relationships.
If the Purview collections look like this:

![Collections](../img/tutorial/create-collections/image06.png)

Example 1: Create a collection hierarchy under `My-Company`. `subcoll1` would be a child under `My-Company`, `subcoll2` would be a child under `subcoll1` (referenced by the `/`), and `sub coll 3` would be a child under `subcoll 2`
```Python
client.create_collections(start_collection="My-Company", 
                          collection_names="subcoll1/subcoll2/sub coll 3"
                        )
```
![Collections](../img/tutorial/create-collections/image07.png)
