
from sys import api_version
from tracemalloc import start
import requests
import random
import re 
import random 
import string

class PurviewCollections():
    def __init__(self, purview_account_name, auth=None):
        self.purview_account_name = purview_account_name
        self.auth = auth.get_access_token()
        self.header = {
            "Authorization": f"Bearer {self.auth}",
            "Content-Type": "application/json"
        }
        self.collections_endpoint = f"https://{self.purview_account_name}.purview.azure.com/account/collections"
        self.collections_api_version = "2019-11-01-preview"
        self.catalog_endpoint = f"https://{self.purview_account_name}.purview.azure.com/catalog"
        self.catalog_api_version = "2022-03-01-preview"

        

    def list_collections(self, only_names: bool = False, api_version: str = None) -> dict:
        """
        Returns a list of dictionaries of the collections you have access to in Purview. Default will display all of the collection info.

        :param only_names: (optional) Bool. Default is False. Returns a dictionary of the actual collection name, friendly name, and parent name.
                If True, will return a dictionary of all the collections with the key being the 
                actual collection name followed by the friendly name and parent collection name.
                If you wish to print the dictionary to the screen in a formatted way and still maintain the hierarcy, 
                import pprint and use: pprint(list_collections, only_names=True), sort_dicts=False) 
        :param api_version (optional) String. Default is None. If None, it uses the self.collections_api_version which is "2019-11-01-preview".
        :return: Dict of the collections 
        :rtype: Dict 
        """

        if not api_version:
            api_version = self.collections_api_version

        url = f"{self.collections_endpoint}?api-version={api_version}"
        collection_request = requests.get(url=url, headers=self.header)
        collections = collection_request.json()['value']
        
        if only_names:
            coll_dict = {}
            for coll in collections:
                if "parentCollection" not in coll:
                    coll_dict[coll['name']] = {
                        "friendlyName": coll['friendlyName'],
                        "parentCollection": None
                    }
                else:
                    coll_dict[coll['name']] = {
                        "friendlyName": coll['friendlyName'],
                        "parentCollection": coll["parentCollection"]['referenceName']
                    }
            return coll_dict
        
        return collections



    def _return_real_collection_name(self, collection_name: str, api_version, force_actual_name: bool = False):
        """
        Internal helper function. Do not call directly.
        """  

        collections = self.list_collections(only_names=True, api_version=api_version)
        friendly_names = ([(name, collections[name])
                                    for name, value in collections.items()
                                    if collection_name == value['friendlyName']])

        if collection_name not in collections and len(friendly_names) == 0:
            err_msg = ("start_collection parameter value error. "
                        f"The collection '{collection_name}' either doesn't exist or your don't have permission to start on it. "
                        "Would need to be a collection admin on that collection if it exists. Name is case sensitive.")
            raise ValueError(err_msg)
        elif collection_name not in collections and len(friendly_names) == 1:
            return friendly_names[0][0]
        elif collection_name in collections and len(friendly_names) <= 1:
            return collection_name
        if force_actual_name:
            for i in range(len(friendly_names)):
                if friendly_names[i][0] == collection_name:
                    return collection_name
        else:
            newline = '\n'
            err_msg = ("collection_name parameter value error. "
                        f"Multiple collections exist with the friendly name '{collection_name}'. "
                        "Please choose and re-enter the first item from one of the tuples below to the collection_name parameter: "
                        f"{newline}{newline.join(map(str,friendly_names))} {newline}"
                        f"If you want to use the collection name '{collection_name}' add the force_actual_name parameter to True. "
                        "Ex: force_actual_name=True")
            raise ValueError(err_msg)



    def _return_request_info(self, name, friendly_name, parent_collection, api_version):
        """
        Internal helper function. Do not call directly.
        """

        url = f'{self.collections_endpoint}/{name}?api-version={api_version}'
        data = f'{{"parentCollection": {{"referenceName": "{parent_collection}"}}, "friendlyName": "{friendly_name}"}}'
        request = requests.put(url=url, headers=self.header, data=data)
        
        return request




    def _return_friendly_collection_names(self, collection_name: str, api_version: str = None):
        """
        Internal helper function. Do not call directly.
        """
        collections = self.list_collections(only_names=True, api_version=api_version)
        friendly_names = ([(name, collections[name])
                                       for name, value in collections.items()
                                       if collection_name == value['friendlyName']])
        return friendly_names



    def _verify_collection_name(self, collection_name: str) -> str:
        """
        Checks to see if the collection_name meets the Purview naming requirements.
        If not, it generates a six character lowercase string (matches what the Purview UI does).
        
        :param collection_name: String.
        :return: Either the original collection_name or a random six character lowercase string if the name doesn't meet the requirements. 
        :rtype: String 
        """

        pattern = "[a-zA-Z0-9]+"
        collection_check = re.search(pattern, collection_name)
        if collection_check:
            collection_name_check = collection_check.group() # returns the name the pattern matched. 
            if len(collection_name) < 3 or len(collection_name) > 36 or (collection_name_check != collection_name):
                collection_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        else:
            collection_name = ''.join(random.choices(string.ascii_lowercase, k=6))
        
        return collection_name



    def _return_updated_collection_name(self, name, collection_dict, parent_collection, friendly_names, api_version):
        """
        Internal helper function. Do not call directly.
        """

        if name in collection_dict and collection_dict[name]['parentCollection'] == parent_collection.lower():
            return name 
        elif name in friendly_names:
            friendly_list = self._return_friendly_collection_names(name, api_version)

            if len(friendly_list) == 1 and friendly_list[0][1]['parentCollection'] == parent_collection.lower():
                name = friendly_list[0][0]
            elif len(friendly_list) == 1 and name in collection_dict:
                name = ''.join(random.choices(string.ascii_lowercase, k=6))

            elif len(friendly_list) > 1:
                for collection in friendly_list:
                    if collection[1]['parentCollection'] == parent_collection.lower():
                        name = collection[0]
                    else:
                        if collection[0] == name:
                            name = ''.join(random.choices(string.ascii_lowercase, k=6))
            else:
                name = self._verify_collection_name(name)

        else:
            name = self._verify_collection_name(name)
        
        return name
        


    def _return_updated_collection_list(self, start_collection, collection_list, collection_dict, api_version):
        """
        Internal helper function. Do not call directly.
        """

        updated_list = []
        friendly_names = [v['friendlyName'] for v in collection_dict.values()]

        for index, name in enumerate(collection_list):
            if index == 0:
                name = self._return_updated_collection_name(name, collection_dict, start_collection, friendly_names, api_version)
            else:
                name = self._return_updated_collection_name(name, collection_dict, updated_list[index - 1], friendly_names, api_version)
            updated_list.append(name)
        
        return updated_list




    def create_collections(self, start_collection: str, collection_names: list[str], force_actual_name: bool = False, api_version: str = None): 
        """
        Create a collection or several collections in Purview. Can do any of following:
            -Create one collection
            -Create multiple collections
            -Create one collection hierarchy (multiple parent child relationships)
            -Create multiple collection hierarchies
        
        :param start_collection: String. Existing collection name to start creating the collections from. 
                Can either pass in the actual Purview collection name or the friendly collection name.
                If you pass in the friendly name and duplicate friendly names exist, you'll receive a friendly error
                asking which collection you'd like to use. This collection has to exist already in Purview.  
        :param collection_names: List of Strings list[str]. As mentioned above, you can pass in as many as needed.
                examples:
                -One collection: pur.create_collections('startcollname', ['mynewcollection'])
                -Multiple collections: pur.create_collections('startcollname', ['mynewcollection', 'mynewcollectiontwo'])
                -Create one collection hierarchy: pur.create_collections('startcollname', ['mynewcollection/mysubcoll1/mysubcoll2'])
                    The / is the parent child relationship. mysubcoll1 would be a child of mynewcollection. 
                    mysubcoll2 would be a child of mysubcoll1.
                -Create multiple collection hierarchies: pur.create('startcollname', ['mynewcollection/mysubcoll1', 'mysecondcollection/mysubcoll2'])
                    The internal code will handle any Purview name requirements. my new collection is a valid name to pass in.
        :param force_actual_name: String. Edge Case. If a friendly name is passed in the start_collection parameter 
                and that name is duplicated across multiple hierarchies and one of those names is the actual passed in name, if True, this will force
                the method to use the actual name you pass in if it finds it.
                examples:
                -If startcollname is passed in the start_collection parameter and that name exists under multiple hierarchies (friendly names)
                if one of the actual names (not friendly name) is startcollname, then it will force the code to use the startcollname. 
        :param api_version (optional): String. Default is None. If None, it uses the self.collections_api_version which is "2019-11-01-preview".
        :return: None
        :rtype None
        """

        if not api_version:
            api_version = self.collections_api_version
        
        coll_dict = self.list_collections(only_names=True, api_version=api_version)
        start_collection = self._return_real_collection_name(start_collection, api_version, force_actual_name)
    
        collection_names_list = [[name] for name in collection_names]
        collection_list = []
        for item in collection_names_list:
            for name in item:
                if "/" in name:
                    names = name.split("/")
                    names = [name.strip() for name in names]
                    collection_list.append(names)
                else:
                    names = [name.strip() for name in item]
                    collection_list.append(names)
        
        for colls in collection_list:
            updated_collection_list = self._return_updated_collection_list(start_collection, colls, coll_dict, api_version)
            for index, name in enumerate(updated_collection_list):
                if index == 0:
                    if name in coll_dict and coll_dict[name]['parentCollection'].lower() == start_collection.lower():
                        continue
                    else:
                        friendly_name = colls[index]

                    try:
                        request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=start_collection, api_version=api_version)
                        print(request.content)
                        print('\n')
                    except Exception as e:
                        raise e

                else:
                    if name in coll_dict and coll_dict[name]['parentCollection'].lower() == updated_collection_list[index - 1].lower():
                        continue
                      
                    else:
                        friendly_name = colls[index]
                        parent_collection = updated_collection_list[index - 1]
                
                    try:
                        request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=parent_collection, api_version=api_version)
                        print(request.content)
                        print('\n')
                    except Exception as e:
                        raise e


    # Delete collections/assets




    def delete_collections(self, collection_names: list[str], force_actual_name: bool = False, api_version: str = None):
        """ Can delete one or more collections. Can pass in either the actual or friendly collection name."""

        if not api_version:
            api_version = self.collections_api_version
        for name in collection_names:
            coll_name = self._return_real_collection_name(name, force_actual_name)   
            url = f"{self.collections_endpoint}/{coll_name}?api-version={api_version}"
            try:
                delete_collections_request = requests.delete(url=url, headers=self.header)
                if not delete_collections_request.content:
                    print(f"The collection '{name}' was successfully deleted")
                else:
                    print(delete_collections_request.content)
            except Exception as e:
                raise e
    

    def get_child_collection_names(self, collection_name: str, api_version: str = None):
        if not api_version:
            api_version = self.collections_api_version
        url = f"{self.collections_endpoint}/{collection_name}/getChildCollectionNames?api-version={api_version}"
        try:
            get_collections_request = requests.get(url=url, headers=self.header)
        except Exception as e:
            raise e
        return get_collections_request.json()


    def _recursive_append(self, name, append_list):
            child_collections = self.get_child_collection_names(name)
            if child_collections['count'] == 0:
                append_list.append(None)
            elif child_collections['count'] == 1:
                append_list.append(child_collections['value'][0]['name'])
            elif child_collections['count'] > 1:
                for v in child_collections.values():
                    if isinstance(v, list):
                        for index, name in enumerate(v):
                            append_list.append(v[index]['name'])


    def delete_collections_recursively(self, collection_names: list[str], also_delete_first_collection: bool = False, api_version: str = None):
        if not api_version:
            api_version = self.collections_api_version
        delete_list = []
        recursive_list = []
        for name in collection_names:
            name = self._return_real_collection_name(name)
            self._recursive_append(name, delete_list)
            if delete_list[0] is not None:
                for item in delete_list:
                        self._recursive_append(item, recursive_list)
                for item2 in recursive_list:
                    if item2 is not None:
                        delete_list.append(item2)
                        self._recursive_append(item2, recursive_list)
        else:
            if delete_list[0] is not None:
                if also_delete_first_collection:
                    delete_list.insert(0, collection_names[0])
                for coll in delete_list[::-1]: # starting from the most child collection
                    self.delete_collections([coll])
        
        
    
    def delete_collection_assets(self, collection_names: list[str], api_version: str = None, force_actual_name: bool = False):
        if not api_version:
            api_version = self.catalog_api_version
        
        # delete all assets in a collection
        for name in collection_names:
            collection = self._return_real_collection_name(name, force_actual_name)
            # url = f"{self.catalog_endpoint}/api/search/query?api-version={api_version}"
            # data = f'{{"keywords": null, "limit": 1, "filter": {{"collectionId": "{collection}"}}}}'       
            # asset_request = requests.post(url=url, data=data, headers=self.header)
            # results = asset_request.json()
            # total = len(results['value'])
            # print(total)

            # # delete entities
            # guids = [item["id"] for item in results["value"]]
            # guid_str = '&guid='.join(guids)
            # url = f"{self.catalog_endpoint}/api/atlas/v2/entity/bulk?guid={guid_str}"
            # request2 = requests.delete(url, headers=self.header)
            # print(request2.content)


            final = False
            while not final:
                url = f"{self.catalog_endpoint}/api/search/query?api-version={api_version}"
                data = f'{{"keywords": null, "limit": 1000, "filter": {{"collectionId": "{collection}"}}}}'       
                asset_request = requests.post(url=url, data=data, headers=self.header)
                results = asset_request.json()
                total = len(results['value'])
                if total == 0:
                    print('total', total)
                    final = True
                    print('end')
                else:
                    # delete entities
                    guids = [item["id"] for item in results["value"]]
                    guid_str = '&guid='.join(guids)
                    url = f"{self.catalog_endpoint}/api/atlas/v2/entity/bulk?guid={guid_str}"
                    request2 = requests.delete(url, headers=self.header)
                    print(request2.content)





  
    # def _start_collection_check(self, start_collection: str, collection_dict: dict, api_version:str = None) -> str:
    #     if start_collection not in collection_dict.keys():
    #         start_collection_check = self._return_real_collection_name(start_collection, api_version)
    #         if len(start_collection_check) == 0:
    #             err_msg = ("start_collection parameter value error. "
    #                         f"The collection '{start_collection}' either doesn't exist or your don't have permission to start on it. "
    #                         "Would need to be a collection admin on that collection if it exists. Name is case sensitive.")
    #             raise ValueError(err_msg) 
            
    #         elif len(start_collection_check) == 1:
    #             start_collection = start_collection_check[0][0] # returns the real name
            
    #         else:
    #             newline = '\n'
    #             err_msg = ("start_collection parameter value error. "
    #                         f"Multiple collections exist with the friendly name '{start_collection}'. "
    #                         "Please choose and re-enter the first item from one of the tuples below to the start_collection parameter: "
    #                         f"{newline}{newline.join(map(str,start_collection_check))}")
    #             raise ValueError(err_msg)
    #     return start_collection










   # def _return_real_collection_name(self, collection_name: str, api_version):
    #     # collections = self._get_collection_info()

    #     collections = self.list_collections(only_names=True, api_version=api_version)
    #     if collection_name in collections.keys():
    #         return collection_name
    #     else:
    #         friendly_names = ([(name, collections[name])
    #                                    for name, value in collections.items()
    #                                    if collection_name == value['friendlyName']])
    #         return friendly_names









    
    
    
    #   def delete_collections(self, collection_names: str, force_actual_name: bool = False, api_version: str = None):
    #     if api_version:
    #         self.api_version = api_version
    #     coll_name = self._return_real_collection_name(collection_names)
    #     if isinstance(coll_name, list):
    #         if len(coll_name) == 1:
    #             coll_name = coll_name[0][0]
    #         else:
    #             newline = '\n'
    #             err_msg = ("collection_names parameter value error. "
    #                         f"Multiple collections exist with the friendly name '{collection_names}'. "
    #                         "Please choose and re-enter the first item from one of the tuples below to the collection_names parameter: "
    #                         f"{newline}{newline.join(map(str,coll_name))}")
    #             raise ValueError(err_msg)
    #     else:
    #         coll_name = collection_names
            
    #     url = f"{self.collections_endpoint}/{coll_name}?api-version={self.api_version}"
    #     try:
    #         delete_collections_request = requests.delete(url=url, headers=self.header)
    #         print(f"The collection {coll_name} was successfully deleted")
    #     except Exception as e:
    #         raise e  
    
    
    
    
    
    
    # def recursive_append(self, name, append_list):
    #     child_collections = self.get_child_collection_names(name)
    #     if child_collections['count'] == 0:
    #         append_list.append('This is it')
    #     elif child_collections['count'] == 1:
    #         append_list.append(child_collections['value'][0]['name'])
    #     elif child_collections['count'] > 1:
    #         for v in child_collections.values():
    #             if isinstance(v, list):
    #                 for index, name in enumerate(v):
    #                     append_list.append(v[index]['name'])
                        
            
            
            
            
            
            
            
        #     while count != 0:
        #         child_collections = self.get_child_collection_names(name)
        #         if child_collections['count'] > 1:
        #             # print(child_collections)
        #             for values in child_collections.values():
        #                 if isinstance(values, list):
        #                     recursive_list.append([name['name'] for name in values])
        #                     count += 1

        # print(recursive_list)
                # for v in child_collections.values():
                #     print(v)
        #         if child_collections['count'] != 0:
        #             if child_collections['count'] == 1:
        #                 recursive_list.append(child_collections['value'][0]['name'])
        #             elif child_collections['count'] > 1:


        # print(recursive_list)


                








        # for name in delete_list[::-1]: # starts from the last item of the list    
        #     url = f"{self.collections_endpoint}/{name}?api-version={self.api_version}"
        #     delete_collections_request = requests.delete(url=url, headers=self.header)
        #     print(delete_collections_request.content)








        # friendly_names = [f['friendlyName'] for f in coll_dict.values()]

        # for coll in collection_list:
        #     for index, name in enumerate(coll):
        #         if index == 0:
        #             # print(coll)
        #             if name in coll_dict.keys():
        #                 friendly_name = coll_dict[name]['friendlyName']
                      
        #             elif name not in coll_dict.keys() and name not in friendly_names:
        #                 friendly_name = name 
                    
        #             elif name not in coll_dict.keys() and name in friendly_names:
        #                 friendly_list = self._return_real_collection_name(name)
        #                 if len(friendly_list) == 1:
        #                     name = friendly_list[0][0]
        #                     friendly_name = friendly_list[0][1]['friendlyName'] 
        #                 else:
        #                     for collection in friendly_list:
        #                         if collection[1]['parentCollection'] == start_collection.lower():
        #                             name = collection[0]
        #                             friendly_name = collection[1]['friendlyName']
                    
        #             try:
        #                 request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=start_collection)
        #                 print(request.content)
        #                 print('\n')
        #             except Exception as e:
        #                 raise e
                
        #         else:
        #             updated_coll_dict = self._get_collection_info()
        #             updated_friendly_names = [f['friendlyName'] for f in updated_coll_dict.values()]
        #             if name in updated_coll_dict.keys():
        #                 # print('here key', updated_coll_dict[name])
        #                 friendly_name = updated_coll_dict[name]['friendlyName']
        #                 parent_collection = self._return_real_collection_name(coll[index - 1])
        #                 if len(parent_collection) > 1:
        #                     for collection in parent_collection:
        #                         if collection[1]['parentCollection'] == 'a':
        #                             pass

        #                 # parent_collection = updated_coll_dict[name]['parentCollection']
        #                 # print(parent_collection, 'testsetset')

        #             elif name not in updated_coll_dict.keys() and name not in updated_friendly_names:
        #                 # print('here22222', name)
        #                 friendly_name = name
        #                 # print(coll)
        #                 parent_collection = coll[index - 1] 
        #                 # print(parent_collection)
        #                 parent_collection2 = self._return_real_collection_name(collection_name=parent_collection2)
        #                 # print(parent_collection)
            
                    # try:
                    #     request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=parent_collection)
                    #     print(request.content)
                    #     print('\n')
                    # except Exception as e:
                    #     raise e
            




# def create_collections(self, start_collection: str, collection_names: list[str] = None):
#         coll_dict = self._get_collection_info()

#         # checks if the start_collection param currently exits. 
#         for name, value in coll_dict.items():
#             if start_collection == name or start_collection == value['friendlyName']:
#                 start_collection_check = True
#                 break
#         if not start_collection_check:
#             raise ValueError(f"The collection '{start_collection}' either doesn't exist or you don\'t have permission to start on it. Would need to be a collection admin on that collection if it exists.")


#         for name in collection_names:
#             if "/" in name:
#                 names = name.split("/")
#                 names = [name.strip() for name in names]
#             else:
#                 names = [name.strip()]
        
    
#         final_dict = {}
#         for item in names:
#             for name, value in coll_dict.items():
#                 friendly_name = value['friendlyName']
#                 # parent_collection = value['parentCollection']
#                 # print(name, friendly_name)
                
#                 if item == name or item == friendly_name:
#                     final_dict[name] = [friendly_name, True]
                
#                 elif item != name or item != friendly_name:
#                     # print(item)
#                     final_dict[item] = [item, False]

#         friendly_names = []
#         real_names = []
#         for key, value in coll_dict.items():
#             friendly_names.append(value['friendlyName'])
#             real_names.append(key)

#         for k,v in final_dict.copy().items(): 
#             if v[0] in friendly_names and v[1] is False:
#                 del final_dict[k]
        
#         print(final_dict)
        

#         for key, value in final_dict.copy().items():
#             exists_in_purview_check = value[1]
#             if not exists_in_purview_check:
#                 new_name = ''.join(random.choices('aen34c', k=6))
#                 final_dict[new_name] = final_dict[key]
#                 final_dict.pop(key)
        
#         dict_keys = list(final_dict.keys())
#         for index, (key, value) in enumerate(final_dict.items()):
#             name = key 
#             friendly_name = value[0]
#             exists_in_purview = value[1]

#             if index == 0 and exists_in_purview is False:
#                 url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
#                 data = f'{{"parentCollection": {{"referenceName": "{start_collection}"}}, "friendlyName": "{friendly_name}"}}'
#                 coll_request = requests.put(url=url, headers=self.header, data=data)
#                 print(coll_request.content)

#             elif exists_in_purview is True:
#                 continue 

#             else:
#                 url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
#                 data = f'{{"parentCollection": {{"referenceName": "{dict_keys[index - 1]}"}}, "friendlyName": "{friendly_name}"}}'
#                 coll_request = requests.put(url=url, headers=self.header, data=data)
#                 print(coll_request.content)











             # if start_collection not in coll_dict.keys():
        #     start_collection_check = self._return_real_collection_name(start_collection)
        #     if len(start_collection_check) == 0:
        #         err_msg = ("start_collection parameter value error. "
        #                    f"The collection '{start_collection}' either doesn't exist or your don't have permission to start on it. "
        #                    "Would need to be a collection admin on that collection if it exists. Name is case sensitive.")
        #         raise ValueError(err_msg) 
            
        #     elif len(start_collection_check) == 1:
        #         start_collection = start_collection_check[0][0] # returns the real name
            
        #     else:
        #         newline = '\n'
        #         err_msg = ("start_collection parameter value error. "
        #                    f"Multiple collections exist with the friendly name '{start_collection}'. "
        #                    "Please choose and re-enter the first item from one of the tuples below to the start_collection parameter: "
        #                    f"{newline}{newline.join(map(str,start_collection_check))}")
        #         raise ValueError(err_msg)
            
            
            
            
            
            
            # if index == 0 and name in coll_dict.keys():
            #     try:
            #         request = self._return_request_info(name=name, friendly_name=coll_dict[name], parent_collection=start_collection)
            #         print(request.content)
            #     except Exception as e:
            #         raise e

            # elif index == 0 and name not in coll_dict.keys() and name not in friendly_names:
            #     try:
            #         request = self._return_request_info(name=name, friendly_name=name, parent_collection=start_collection)
            #         print(request.content)
            #     except Exception as e:
            #             raise e  
            
            # elif index == 0 and name not in coll_dict.keys() and name in friendly_names:
            #     value = self._return_real_collection_name(name)
            #     # print(value)
            #     # print(value[0][1]['parentCollection'])
            #     if len(value) == 1:
            #         name = value[0][0]
            #         friendly_name = name
            #     else:
            #         for item in value:
            #             if item[1]['parentCollection'] == start_collection.lower():
            #                 name = item[0]
            #                 friendly_name = item[1]['friendlyName']
            #     try:
            #         request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=start_collection)
            #         # print(name)
            #         print(request.content)
            #     except Exception as e:
            #         raise e
                         

            # else:
            #     if name in friendly_names:
            #         parent = names[index - 1]
            #         value = [(name, coll_dict['friendlyName'], coll_dict['parentCollection']) for name, value in coll_dict.items() if name == parent)]
            #         print('name is in friendly names', name)
            #     try:
            #         request = self._return_request_info(name=name, friendly_name=name, parent_collection=names[index - 1])
            #         print(request.content)
            #     except Exception as e:
            #         raise e






                    # try:
                    #     url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
                    #     data = f'{{"parentCollection": {{"referenceName": "{start_collection}"}}, "friendlyName": "{coll_dict[name]["friendlyName"]}"}}'
                    #     coll_request = requests.put(url=url, headers=self.header, data=data)
                    #     print(coll_request.content)
                    # except Exception as e:
                    #     raise e
            
            
                #     url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
                #     data = f'{{"parentCollection": {{"referenceName": "{start_collection}"}}, "friendlyName": "{name}"}}'
                #     coll_request = requests.put(url=url, headers=self.header, data=data)
                #     print(coll_request.content)
                # except Exception as e:
                #         raise e


        # for item in names:
        #     for name, value in coll_dict.items():
        #         friendly_name = value['friendlyName']
        #         # parent_collection = value['parentCollection']
        #         # print(name, friendly_name)
                
        #         if item == name:
        #             print(name, value['friendlyName'], value['parentCollection'])
        #             final_dict[name] = [friendly_name, True]
                
        #         else:
        #             # print(item)
        #             final_dict[item] = [item, False]

        # # print(final_dict)
        
        
        # friendly_names = []
        # real_names = []
        # for key, value in coll_dict.items():
        #     friendly_names.append(value['friendlyName'])
        #     real_names.append(key)

        # for k,v in final_dict.copy().items(): 
        #     if v[0] in friendly_names and v[1] is False:
        #         del final_dict[k]
        
        # # print(final_dict)
        

        # for key, value in final_dict.copy().items():
        #     exists_in_purview_check = value[1]
        #     if not exists_in_purview_check:
        #         new_name = ''.join(random.choices('aen34c', k=6))
        #         final_dict[new_name] = final_dict[key]
        #         final_dict.pop(key)
        
        # dict_keys = list(final_dict.keys())
        # for index, (key, value) in enumerate(final_dict.items()):
        #     name = key 
        #     friendly_name = value[0]
        #     exists_in_purview = value[1]

        #     if index == 0 and exists_in_purview is False:
        #         url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
        #         data = f'{{"parentCollection": {{"referenceName": "{start_collection}"}}, "friendlyName": "{friendly_name}"}}'
        #         coll_request = requests.put(url=url, headers=self.header, data=data)
        #         print(coll_request.content)

        #     elif exists_in_purview is True:
        #         continue 

        #     else:
        #         url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
        #         data = f'{{"parentCollection": {{"referenceName": "{dict_keys[index - 1]}"}}, "friendlyName": "{friendly_name}"}}'
        #         coll_request = requests.put(url=url, headers=self.header, data=data)
        #         print(coll_request.content)



   # def _get_collection_info(self, api_version=None):
    #     collection_list = self.list_collections(api_version=api_version)
    #     coll_dict = {}
    #     for coll in collection_list:
    #         if "parentCollection" not in coll:
    #             coll_dict[coll['name']] = {
    #                 "friendlyName": coll['friendlyName'],
    #                 "parentCollection": None
    #             }
    #         else:
    #             coll_dict[coll['name']] = {
    #                 "friendlyName": coll['friendlyName'],
    #                 "parentCollection": coll["parentCollection"]['referenceName']
    #             }
    #     return coll_dict



    # def _return_updated_collection_list(self, start_collection, collection_list, collection_dict): # old one
    #     updated_list = []
    #     friendly_names = [v['friendlyName'] for v in collection_dict.values()]
    #     for index, name in enumerate(collection_list):
    #         if index == 0:
    #             if name in collection_dict.keys(): 
    #                 if collection_dict[name]['parentCollection'] == start_collection.lower():
    #                     updated_list.append(name)
    #                 elif name in friendly_names:
    #                     friendly_list = self._return_friendly_collection_names(name)
    #                     if len(friendly_list) == 1:
    #                         if friendly_list[0][1]['parentCollection'] == start_collection.lower():
    #                             name = friendly_list[0][0]
    #                             updated_list.append(name)
    #                         else:
    #                             name = ''.join(random.choices(string.ascii_letters, k=6))
    #                             updated_list.append(name)
    #                     elif len(friendly_list) > 1:
    #                         for collection in friendly_list:
    #                             if collection[1]['parentCollection'] == start_collection.lower():
    #                                 name = collection[0]
    #                                 updated_list.append(name)
                                
    #             elif name not in collection_dict.keys() and name in friendly_names:
    #                 friendly_list = self._return_real_collection_name(name)
    #                 if type(friendly_list) == str:
    #                     updated_list.append(name)
    #                 elif len(friendly_list) == 1:
    #                     if friendly_list[0][1]['parentCollection'] == start_collection.lower():
    #                         name = friendly_list[0][0]
    #                         updated_list.append(name)
    #                     else:
    #                         name = ''.join(random.choices(string.ascii_letters, k=6))
    #                         updated_list.append(name)
    #                 elif len(friendly_list) > 1:
    #                     for collection in friendly_list:
    #                         if collection[1]['parentCollection'] == start_collection.lower():
    #                             name = collection[0]
    #                             updated_list.append(name)
    #                     # else:
    #                     #     raise ValueError("friendly name not matching parent start collection")
    #             else:
    #                 name = self._verify_collection_name(name)
    #                 updated_list.append(name)
            
    #         else:
    #             if name in collection_dict.keys():
    #                 if collection_dict[name]['parentCollection'] == updated_list[index - 1].lower():
    #                     updated_list.append(name)
    #                 else:
    #                     name = ''.join(random.choices(string.ascii_letters, k=6))
    #                     updated_list.append(name)
                
    #             elif name not in collection_dict.keys() and name in friendly_names:
    #                 friendly_list = self._return_real_collection_name(name)
    #                 if type(friendly_list) == str:
    #                     updated_list.append(name)
    #                 elif len(friendly_list) == 1:
    #                     name = friendly_list[0][0]
    #                     updated_list.append(name)
    #                 elif len(friendly_list) > 1:
    #                     for collection in friendly_list:   
    #                         if collection[1]['parentCollection'] == updated_list[index - 1].lower():
    #                                     name = collection[0]
    #                                     updated_list.append(name)
    #             else:
    #                 name = self._verify_collection_name(name)
    #                 updated_list.append(name)
    #     return updated_list
    

    # def create_collections(self, start_collection: str, collection_names: list[str]): # old one
    #     coll_dict = self._get_collection_info()
        
    #     print(coll_dict)
    #     print('\n')

    #     start_collection = self._start_collection_check(start_collection=start_collection, collection_dict=coll_dict)
    
    #     collection_names_list = [[name] for name in collection_names]
    #     collection_list = []
    #     for item in collection_names_list:
    #         for name in item:
    #             if "/" in name:
    #                 names = name.split("/")
    #                 names = [name.strip() for name in names]
    #                 collection_list.append(names)
    #             else:
    #                 names = [name.strip() for name in item]
    #                 collection_list.append(names)
        
    #     for colls in collection_list:
    #         updated_collection_list = self._return_updated_collection_list(start_collection, colls, coll_dict)
    #         for index, name in enumerate(updated_collection_list):
    #             if index == 0:
    #                 if name in coll_dict.keys():
    #                     friendly_name = coll_dict[name]['friendlyName']
                    
    #                 elif name not in coll_dict.keys():
    #                     friendly_name = colls[index] 

    #                 try:
    #                     request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=start_collection)
    #                     print(request.content)
    #                     print('\n')
    #                 except Exception as e:
    #                     raise e

    #             else:
    #                 if name in coll_dict.keys():
    #                     friendly_name = coll_dict[name]['friendlyName']
    #                     parent_collection = updated_collection_list[index - 1]
                    
    #                 elif name not in coll_dict.keys():
    #                     friendly_name = colls[index]
    #                     parent_collection = updated_collection_list[index - 1] 
                
    #                 try:
    #                     request = self._return_request_info(name=name, friendly_name=friendly_name, parent_collection=parent_collection)
    #                     print(request.content)
    #                     print('\n')
    #                 except Exception as e:
    #                     raise e

    def test2(self):
        import json
        url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/test8889-?api-version=2019-11-01-preview'
        data = {"parentCollection": {"referenceName": "sap"}, "friendlyName": "test-8889"}
        print(data)
        coll_request = requests.put(url=url, headers=self.header, data=json.dumps(data))
        print(coll_request.content)




