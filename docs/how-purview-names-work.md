## **Purview Collection Names Overview**

When a collection is created in Purview, there are two names assigned to the collection:

1. The **actual name** (what we will call it for this tutorial and throughout the docs) 
2. The **friendly name**

After creating a collection using the Purview UI, the name displayed is the **friendly name**. Under the hood, Purview stores the **actual name** as a random six character string. This avoids collection name collision. 

In the below example in the Purview UI, a collection name is displayed as `My-Collection`:
![How collection names work](../img/how-purview-names-work/image01.png)

But under the hood, the actual name is `1nlmts` and the friendly name is `My-Collection`:
![How collection names work](../img/how-purview-names-work/image02.png)

This is important because if you tried to create a child collection under `My-Collection` using the [Purview Collection REST API](https://learn.microsoft.com/en-us/rest/api/purview/catalogdataplane/collection/create-or-update?tabs=HTTP) and used `My-Collection` as the parent collection reference, it would return an error stating `My-Collection` doesn't exist.

You'd have to first find the actual name of My-Collection (`1nlmts`) and then can create the collection. This can get very tricky when trying to create collections and collection hierarchies.

Actual names have to be unique across the entire Purview account but friendly names can be duplicated in different hierarchies (can't be duplicated in the same hierarchy).

For example, the friendly name `My-Collection` is used under two different hierarchies:
![How collection names work](../img/how-purview-names-work/image03.png)

But the actual names are different:
![How collection names work](../img/how-purview-names-work/image04.png)
 

## **Handeling Names and Duplicate Multiple Friendly Names**
Fortunately, using purviewautomation, you can pass in either the **actual name** or the **friendly name** of the collection. It handles both! 

In the event there's multiple duplicate friendly names, see: [Handling Duplicate Purview Friendly Names and Edge Cases](handeling-multiple-duplicate-friendly-names.md)