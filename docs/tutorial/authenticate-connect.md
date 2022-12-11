


<!-- ![Nav tabs enabled](../img/create-purview/image01.png) -->


### **Overview **

There are two main ways to authenticate/connect to Purview:

1. [Authenticating with a Service Principal](#authenticating-with-a-service-principal)
2. [Authenticating with the azure-identity Python package](#authenticating-with-the-azure-identity-python-package)

### **Authenticating with a Service Principal**
**Not sure how to create a Service Principal or why it's used? See: [Create a Service Principal](../create-a-service-principal.md)**

To authenticate with a Service Principal, import the ServicePrincipalAuthentication and PurviewCollection classes:
```Python
from purviewautomation import (ServicePrincipalAuthentication,
                                   PurviewCollections)
```

Create a variable named **auth** (can be named anything) and add the tenantid and the Service Principal's client id and client secret:

```Python
auth = ServicePrincipalAuthentication(tenantid="yourtenantid",
                                          clientid="yourclientid",
                                          clientsecret="yourclientsecret")
```
!!! tip
    To find the tenantid, go to **[portal.azure.com](https://portal.azure.com)**, sign in and then click on the Azure Active Directory blade on the left. The tenantid will then be displayed in the middle of the screen.

Now create a variable named **client** (can be named anything) and instantiate the class with your Purview account name and the auth variable created in the previous step:

```Python
client = PurviewCollections(purview_account_name=yourpurviewaccountname,
                                auth=auth)
```

Use the client object to interact with the collections. Ex: `print(client.list_collections())`

**Below is a full example (the client id, etc. are made up. Replace them with your info:**
```Python
from purviewautomation import (ServicePrincipalAuthentication,
                                PurviewCollections
)
auth = ServicePrincipalAuthentication(tenantid="12345678",
                                        clientid="12345-6786",
                                        clientsecret="secret1111")

client = PurviewCollections(purview_account_name="purview-demo-1",
                            auth=auth)
```

Now interact with the collections:
```Python
print(client.list_collections())
```



### Authenticating with the azure-identity Python package

To authenticate using the azure-identity Python package, first install the package

```Python
pip install azure-identity
```
!!! Important
    Make sure Azure CLI is also installed. See here for how to install it: [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).

Then sign in with your Azure CLI credentials (open a terminal type `az login` and sign in via the link that pops up.

For example, in Visual Studio Code, select `Terminal` at the top and type `az login` at the bottom:

![Authenticate](../img/tutorial/authenticate/image01.png)


![Authenticate](../img/tutorial/authenticate/image02.png)


Sign into Azure via the link that pops up. Once signed in, create a Python file `main.py` for example and enter in the code and replace `yourpurviewaccountname` with the Purview account name to connect to:

```Python
from azure.identity import AzureCliCredential

from purviewautomation import PurviewCollections, AzIdentityAuthentication

auth = AzIdentityAuthentication(credential=AzureCliCredential())

client = PurviewCollections(purview_account_name="yourpurviewaccountname",
                            auth=auth)
```

Now interact with the collections:
```Python
print(client.list_collections())
```



