### Overview 

::: purviewautomation.collections.PurviewCollections.create_collections
    options:
        heading_level: 0

### Examples
The start_collection has to already exist in Purview. Pass in either the friendly name or the real name of the collection.

Code will automatically trim an leading or training whitespaces.

# Create One collection 
If the Purview collections look like this:

![Collections](../img/tutorial/create-collections/image01.png)

**Create one collection starting from any of the three listed (purview-test-2, My-Company, test 1):**
```Python
client.create_collections(start_collection="purview-test-2", collection_names="new collection 1")
```
This will create a collection under purview-test-2 (same level as the My-Company collection):
![Collections](../img/tutorial/create-collections/image02.png)

**Create from `test 1`. As you can see, `sub test coll` is listed as a child of `test 1`. The keyword arguments can be ommited if desired:**
```Python
client.create_collections("test 1", "sub test coll")
```
![Collections](../img/tutorial/create-collections/image03.png)


# Create Multiple Collections
