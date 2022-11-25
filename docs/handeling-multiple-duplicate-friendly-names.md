## **Handeling Names**
Fortunately, using purviewautomation, you can pass in either the **actual name** or the **friendly name** of the collection. It handles both! 

For additional info on what **actual name** and **friendly name** means, see: [Purview Collection Names Overview](how-purview-names-work.md)  

## **Handling Multiple Duplicate Friendly Names in the collection_names Parameter When Creating Collections**
When passing in a duplicate friendly name in the collection_names parameter to create a single collection or to create a collection hierarchy, the code will automatically handle it. There's nothing extra needed :). 

For example, using the below Purview:

![How collection names work](../img/how-purview-names-work/image10.png)

If trying to create a hierarchy under `Collection 3` and using `duplicatename`:
```Python
client.create_collections(start_collection="Collection 3", 
                          collection_names="duplicatename/random collection 1/random collection 2")
```

The code automatically knows the parent collection and can handle it accordingly (won't raise an error):

![How collection names work](../img/how-purview-names-work/image11.png)


## **Handling Multiple Duplicate Friendly Names in the start_collection Parameter When Creating Collections or When Deleting Collections**

In the event there's multiple duplicate friendly names, either pass in the **actual name** (which has to be unique across Purview) or if a **friendly name** is passed, the code will raise a value error advising you to choose one of the **actual names**.

For example, given the below Purview, `My-Collection` is a duplicated friendly name across two different hierarchies:

![How collection names work](../img/how-purview-names-work/image03.png)

 If creating a collection and `My-Collection` is passed in the start_collection parameter:
```Python
client.create_collections(start_collection="My-Collection", 
                          collection_names="new collection")
``` 

A value error will be raised displaying the options:
![How collection names work](../img/how-purview-names-work/image05.png)
In the above image, the duplicated names are listed. 

Choose which **actual name** to use:

1. **tslfws** if the collection should be under the Collection 1/My-Collection hierarchy
2. **inqtg7** if the collection should be under the Collection 2/My-Collection hierarchy

If choosing the Collection 1/My-Collection hierarchy, run the below code:
```Python
client.create_collections(start_collection="tslfws", 
                          collection_names="new collection")
```
![How collection names work](../img/how-purview-names-work/image06.png)


## **Edge Case: Multiple Duplicate Friendly Names force_actual_name Parameter**
In the rare edge case where there's duplicate friendly names and one of the actual names is also the name that should be used, pass in the force_actual_name parameter as True.

For example, there's a duplicate friendly name called `duplicatename`:
![How collection names work](../img/how-purview-names-work/image07.png)

When running the code: 
!!! info
    This scenario was specifically created for the below error. Most duplicate friendly name situations will not hit this edge case.
```Python
client.create_collections(start_collection="duplicatename",
                          collection_names="new collection")
```

A value error will be raised displaying the duplicate names and to select one:
![How collection names work](../img/how-purview-names-work/image08.png)

In this example, because one of the actual names is the duplicated friendly name `duplicatename`, to create a collection under the actual name `duplicatename` (instead of under `xfypcn`), use the code:
```Python
client.create_collections(start_collection="duplicatename",
                          collection_names="new collection", 
                          force_actual_name=True)
```
This will create the collection under the actual name `duplicatename`:
![How collection names work](../img/how-purview-names-work/image09.png)