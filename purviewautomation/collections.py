
from sys import api_version
import requests
import random
import re 
import random 
import string
from pprint import pprint 
from typing import Union

class PurviewCollections():
    def __init__(self, purview_account_name, auth):
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

        
    
    def list_collections(self, only_names: bool = False, pretty_print: bool = False, api_version: str = None) -> dict:
        """
        Returns a list of dictionaries of the collections you have access to in Purview. Default will display all of the collection info.

        :param only_names: (optional) Bool. Default is False. Returns a dictionary of the actual collection name, friendly name, and parent name.
                If True, will return a dictionary of all the collections with the key being the 
                actual collection name followed by the friendly name and parent collection name.
                If you wish to print the dictionary to the screen in a formatted way and still maintain the hierarcy, 
                import pprint and use: pprint(list_collections, only_names=True), sort_dicts=False) 
        :param pretty_print: (optional) Bool. Default is False. If True, prints out the collections in a sorted order (starting at the root).
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
            if pretty_print:
                pprint(coll_dict, sort_dicts=True)

            return coll_dict
        
        if pretty_print:
            pprint(collections, sort_dicts=True)

        return collections



    def _return_real_collection_name(self, collection_name: str, api_version: str = None, force_actual_name: bool = False):
        """
        Internal helper function. Do not call directly.
        """  
        if not api_version:
            api_version = self.collections_api_version

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
                        f"{newline}{newline.join(map(str, friendly_names))} {newline}"
                        f"If you want to use the collection name '{collection_name}' add the force_actual_name parameter to True. "
                        "Ex: force_actual_name=True")
            raise ValueError(err_msg)



    def get_real_collection_name(self, collection_name: str, api_version: str = None) -> str:
        """
        Pass in a collection name (friendly name or real name) and it returns either no collection found, the real collection name 
        or if there are multiple friendly names, it will print the them as tuples. 
        
        :param collection_name. String. 
        :return:
        :rtype:  
        """
        
        if not api_version:
            api_version = self.collections_api_version
        
        collections = self.list_collections(only_names=True, api_version=api_version)
        friendly_names = ([(name, collections[name])
                                    for name, value in collections.items()
                                    if collection_name == value['friendlyName']])
        
        if collection_name not in collections and len(friendly_names) == 0:
            err_msg = f" The collection '{collection_name}' either doesn't exist or you don't have access to check it."
            raise ValueError(err_msg)
        
        elif collection_name not in collections and len(friendly_names) == 1:
            return friendly_names[0][0]

        elif collection_name in collections and len(friendly_names) <= 1:
            return collection_name
        
        else:
            friendly_parent_names = []
            parent_list = [item[1]['parentCollection'] for item in friendly_names]
            
            for parent in parent_list:
                for name, value in collections.items():
                    if parent == name.lower():
                        friendly_parent_names.append(value['friendlyName'])
            
            multiple_friendly_list = []
            for name, parent in zip(friendly_names, friendly_parent_names):
                multiple_friendly_list.append((name[0], name[1]['friendlyName'], parent))

            newline = '\n'
            message = (f"Multiple collections exist with the friendly name '{collection_name}'. "
                       f"{newline}Below are tuples displaying the real collection name followed by "
                       "the friendly name and the parent collection friendly name (real_name, friendly_name, parent_friendly_name): "
                       f"{newline}{newline.join(map(str, multiple_friendly_list))} {newline}")
            return message



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
        Checks to see if the new collection_name meets the Purview naming requirements.
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




    def create_collections(self, start_collection: str, collection_names: Union[str, list], force_actual_name: bool = False, api_version: str = None, **kwargs): 
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
        :param collection_names: Either a string or a List of Strings list[str]. As mentioned above, you can pass in as many as needed.
                examples:
                -One collection: pur.create_collections('startcollname', 'mynewcollection')
                -Multiple collections: pur.create_collections('startcollname', ['mynewcollection', 'mynewcollectiontwo'])
                -Create one collection hierarchy: pur.create_collections('startcollname', 'mynewcollection/mysubcoll1/mysubcoll2')
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

        collection_list = []
        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list type.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]
     
        collection_names_list = [[name] for name in collection_names]
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
                        if 'safe_delete_friendly_name' in kwargs:
                            friendly_name = kwargs['safe_delete_friendly_name']
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


    def _safe_delete(self, collection_names: list[str], safe_delete_name: str):
        """Helper function. Do not run directly."""

        collections = self.list_collections(only_names=True)

        create_colls_list = []
        for name in collection_names:
            if len(collection_names) == 1:
                collection_name = self._return_real_collection_name(name)
                parent_name = collections[collection_name]['parentCollection']
                friendly_name = collections[collection_name]['friendlyName']
                create_collection_string = f"{safe_delete_name}.create_collections(start_collection='{parent_name}', collection_names='{collection_name}', friendly_name='{friendly_name}')"
            
            else:
                collection_name = self._return_real_collection_name(name)
                parent_name = collections[collection_name]['parentCollection']
                friendly_name = collections[collection_name]['friendlyName']
                create_collection_string = f"create_collections(start_collection='{parent_name}', collection_names='{collection_name}', friendly_name='{friendly_name}')"
                create_colls_list.append(create_collection_string)
        
        print("Copy and run the below code in your program to recreate the collection/collections:", '\n')
        if len(collection_names) == 1:
            print(create_collection_string)
        else:
            for item in create_colls_list:
                create_coll_final_string = f"{safe_delete_name}.{item}"
                print(create_coll_final_string)
        print('\n')
        print('end of code')
        print('\n')




    def _safe_delete2(self, collection_names: list[str], safe_delete_name: str):
        """Helper function. Do not run directly."""

        collections = self.list_collections(only_names=True)

        create_colls_list = []
        for name in collection_names:
            if len(collection_names) == 1:
                collection_name = self._return_real_collection_name(name)
                parent_name = collections[collection_name]['parentCollection']
                create_collection_string = f"{safe_delete_name}.create_collections('{parent_name}', ['{name}'])"
            
            else:
                collection_name = self._return_real_collection_name(name)
                parent_name = collections[collection_name]['parentCollection']
                create_collection_string = f"create_collections('{parent_name}', ['{name}'])"
                create_colls_list.append(create_collection_string)
        
        print("Copy and run the below code in your program to recreate the collections:", '\n')
        if len(collection_names) == 1:
            print(create_collection_string)
        else:
            initial_list = []
            clean_list = []
            for item in create_colls_list:
                create_coll_final_string = f"{safe_delete_name}.{item}"
                create_coll_final_string.append(initial_list)
            clean_list = [clean_list.append(create_coll_string) for create_coll_string in initial_list if create_coll_string not in clean_list]
                # print(create_coll_final_string)
        print('\n')
        print('end of code')
        print('\n')



    def delete_collections(self, collection_names: Union[str, list], safe_delete: str = None, force_actual_name: bool = False, api_version: str = None):
        """ Delete one or more collections. Can pass in either the actual or friendly collection name. No collections that have children"""

        if not api_version:
            api_version = self.collections_api_version

        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list type.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        if safe_delete:
                self._safe_delete(collection_names=collection_names, safe_delete_name=safe_delete)

        for name in collection_names:
            coll_name = self._return_real_collection_name(name, force_actual_name)
            
            child_collections_check = self.get_child_collection_names(coll_name)
            if child_collections_check['count'] > 0:
                err_msg = (f"The collection '{name}' has child collections. Can only delete collections that have no children. "
                           "To delete collections and all of their children recursively, " 
                           f"use: delete_collections_recursively(['{name}'])")
                raise ValueError(err_msg)   
            
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

        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list type.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]
        
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
        
        if delete_list[0] is not None:
            if also_delete_first_collection:
                delete_list.insert(0, collection_names[0])
            for coll in delete_list[::-1]: # starting from the most child collection
                self.delete_collections([coll])



        # for name in collection_names:
        #     name = self._return_real_collection_name(name)
        #     self._recursive_append(name, delete_list)
        #     if delete_list[0] is not None:
        #         for item in delete_list:
        #                 self._recursive_append(item, recursive_list)
        #         for item2 in recursive_list:
        #             if item2 is not None:
        #                 delete_list.append(item2)
        #                 self._recursive_append(item2, recursive_list)
        
        # if delete_list[0] is not None:
        #     if also_delete_first_collection:
        #         delete_list.insert(0, collection_names[0])
        #     for coll in delete_list[::-1]: # starting from the most child collection
        #         self.delete_collections([coll])
        
        
    
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

        


    def test_delete_collections_recursively(self, collection_names: Union[str, list], safe_delete: str = None, also_delete_first_collection: bool = False, api_version: str = None):
        # ['test1']
        
        if not api_version:
            api_version = self.collections_api_version

        delete_list = []
        recursive_list = []
        collections = self.list_collections(only_names=True)

        if not isinstance(collection_names, (str, list)):
            raise ValueError("The collection_names parameter has to either be a string or a list type.")
        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        for name in collection_names:
            parent_name = self._return_real_collection_name(name)
            name = self._return_real_collection_name(name)
            self._recursive_append(name, delete_list)
            if delete_list[0] is not None:
                for item in delete_list:
                        self._recursive_append(item, recursive_list)
                for item2 in recursive_list:
                    if item2 is not None:
                        delete_list.append(item2)
                        self._recursive_append(item2, recursive_list)
        
        if delete_list[0] is not None:
            if also_delete_first_collection:
                delete_list.insert(0, collection_names[0])
        
            
        # if recursive_list[0] is None:
        #     pass
        #     # for coll in delete_list:
        #     #     friendly_name = collections[coll]['friendlyName']
        #     #     create_collection_string = f"{safe_delete}.create_collections('{parent_name}', ['{friendly_name}'])"
        #     #     print(create_collection_string)
        
        else:
            for index, (item, item2) in enumerate(zip(delete_list, recursive_list)):
                if index == 0:
                    # print(parent_name, collections[item]['friendlyName'], collections[item2]['friendlyName'])
                    first_string = f"{safe_delete}.create_collections('{parent_name}', ['{collections[item]['friendlyName']}'])"
                    print(first_string)
                    # print(collections[item]['friendlyName'], collections[item2]['friendlyName'])
            
                else:
                    friendly_parent = collections[delete_list[index - 1]]['friendlyName']
                    coll2 = collections[item]['friendlyName']
                    # print(collections[item]['friendlyName'], collections[delete_list[index - 1]]['friendlyName'])
                    new_string = f"{safe_delete}.create_collections('{friendly_parent}', ['{coll2}'])"
                    print(new_string)
            



    def test_test_delete_collections_recursively(self, collection_names: list[str], safe_delete: str = None, also_delete_first_collection: bool = False, api_version: str = None):
            # ['test1']
            
            if not api_version:
                api_version = self.collections_api_version

            delete_list = []
            recursive_list = []

            if not isinstance(collection_names, (str, list)):
                raise ValueError("The collection_names parameter has to either be a string or a list type.")
            elif isinstance(collection_names, str):
                collection_names = [collection_names]

            for name in collection_names:
                # parent_name = self._return_real_collection_name(name)
                name = self._return_real_collection_name(name)
                self._recursive_append(name, delete_list)
                if delete_list[0] is not None:
                    for item in delete_list:
                            self._recursive_append(item, recursive_list)
                    for item2 in recursive_list:
                        if item2 is not None:
                            delete_list.append(item2)
                            self._recursive_append(item2, recursive_list)
            

            if safe_delete:
                self._safe_delete_recursivly2(delete_list, recursive_list, collection_names, safe_delete, name)

            if delete_list[0] is not None:
                if also_delete_first_collection:
                    delete_list.insert(0, collection_names[0])
                for coll in delete_list[::-1]: # starting from the most child collection
                    self.delete_collections([coll])
            



    def _safe_delete_recursivly(self, delete_list: list[str], recursive_list, collection_names: list[str], safe_delete_name: str, parent_name: str):

        collections = self.list_collections(only_names=True)
        print("Safe Delete. Copy and run the below code in your program to recreate the collections and collection hierarchies:", '\n')
        
        for index, name in enumerate(delete_list):
            if index == 0:
                first_string = f"{safe_delete_name}.create_collections('{parent_name}', ['{collections[name]['friendlyName']}'])"
                print(first_string)

            # if collections[name]['parentCollection'].lower() == parent_name.lower():
            #     print(True)
            child_test = self.get_child_collection_names(name)
                # print(child_test)
            if child_test['count'] == 1:
                print(f"{safe_delete_name}.create_collections('{name}', ['{child_test['value'][0]['name']}'])")
                # friendly_parent = collections[child_test['value'][0]['name']]

            elif child_test['count'] > 1:
                for index, name2 in enumerate(child_test['value']):
                    # print(name2['name'])
                    print(f"{safe_delete_name}.create_collections('{name}', ['{name2['name']}'])")
            else:
                # print(name)
                parent_name = collections[name]['parentCollection']
                # print(collections[name]['friendlyName'], collections[parent_name]['friendlyName'])
                print(f"{safe_delete_name}.create_collections('{parent_name}', ['{collections[name]['friendlyName']}'])")
            
            
            
    def _safe_delete_recursivly2(self, delete_list: list[str], recursive_list, collection_names: list[str], safe_delete_name: str, parent_name: str):
        initial_list = []
        clean_list = []

        print('rec', recursive_list)
        print('delete', delete_list)

        collections = self.list_collections(only_names=True)
        print("Safe Delete. Copy and run the below code in your program to recreate the collections and collection hierarchies:", '\n')
        
        for index, name in enumerate(delete_list):
            if index == 0 or collections[name]['parentCollection'].lower() == parent_name.lower():
                print(name)
                first_string = f"{safe_delete_name}.create_collections(start_collection='{parent_name}', collection_names='{name}', safe_delete_friendly_name='{collections[name]['friendlyName']}')"
                initial_list.append(first_string)

            child_test = self.get_child_collection_names(name)
                # print(child_test)
            if child_test['count'] == 1:
                print(child_test) # need to fix this statement. Collection_names
                initial_list.append(f"{safe_delete_name}.create_collections(start_collection='{name}', collection_names='{child_test['value'][0]['name']}', safe_delete_friendly_name='{child_test['value'][0]['friendlyName']}')")
                # print(f"{safe_delete_name}.create_collections('{name}', ['{child_test['value'][0]['name']}'])")
                # friendly_parent = collections[child_test['value'][0]['name']]

            elif child_test['count'] > 1:
                print('child equals more than 1')
                for index, name2 in enumerate(child_test['value']):
                    initial_list.append(f"{safe_delete_name}.create_collections(start_collection='{name}', collection_names='{name2}, safe_delete_friendly_name='{name2['friendlyName']}'])")

                    # print(f"{safe_delete_name}.create_collections('{name}', ['{name2['name']}'])")
            else:
                parent_name = collections[name]['parentCollection']
                friendly_name = collections[name]['friendlyName']
                initial_list.append(f"{safe_delete_name}.create_collections(start_collection='{parent_name}', collection_names='{name}', safe_delete_friendly_name='{friendly_name}')")
        
        default_set = set()
        for item in initial_list:
            if item not in default_set:
                default_set.add(item)
                clean_list.append(item)
        for item in clean_list:
            print(item)
            
        
            
            # if index == 0:
            #     print(name)
            #     # # print(parent_name, collections[item]['friendlyName'], collections[item2]['friendlyName'])
            #     # first_string = f"{safe_delete_name}.create_collections('{parent_name}', ['{collections[name]['friendlyName']}'])"
            #     # print(first_string)
            #     # child_test = self.get_child_collection_names(name)
            #     # if child_test['count'] == 1:
            #     #     print(f"{safe_delete_name}.create_collections('{name}', ['{child_test['value'][0]['name']}'])")
            #     # elif child_test['count'] > 1:
            #     #     for index, name2 in enumerate(child_test['value']):
            #     #         # print(name2['name'])
            #     #         print(f"{safe_delete_name}.create_collections('{name}', ['{name2['name']}'])")
            #     # else:
            #     #     f"{safe_delete_name}.create_collections('{parent_name}', ['{collections[name]['friendlyName']}'])"

            # else:
            #     child_test = self.get_child_collection_names(name)
            #     # print(child_test)
            #     if child_test['count'] == 1:
            #         print(f"{safe_delete_name}.create_collections('{name}', ['{child_test['value'][0]['name']}'])")
            #         # friendly_parent = collections[child_test['value'][0]['name']]

            #     elif child_test['count'] > 1:
            #         for index, name2 in enumerate(child_test['value']):
            #             # print(name2['name'])
            #             print(f"{safe_delete_name}.create_collections('{name}', ['{name2['name']}'])")
            #     else:
            #         # print(name)
            #         parent_name = collections[name]['parentCollection']
            #         # print(collections[name]['friendlyName'], collections[parent_name]['friendlyName'])
            #         print(f"{safe_delete_name}.create_collections('{parent_name}', ['{collections[name]['friendlyName']}'])")
        print('\n')
        print('end code', '\n')




                    # print(child_test['value'][0]['friendlyName'])
                # print(collections[name]['parentCollection'], delete_list[index - 1], 'herererere')
                # friendly_parent = collections[delete_list[index - 1]]['friendlyName']
                # coll2 = collections[name]['friendlyName']
                # print(collections[item]['friendlyName'], collections[delete_list[index - 1]]['friendlyName'])
                # new_string = f"{safe_delete_name}.create_collections('{friendly_parent}', ['{coll2}'])"
                # print(new_string)        
        # print('\n')
        # print('end code')
        # print('\n')


        



    #  """Helper function. Do not run directly."""

    #     collections = self.list_collections(only_names=True)

    #     create_colls_list = []
    #     for name in collection_names:
    #         if len(collection_names) == 1:
    #             collection_name = self._return_real_collection_name(name)
    #             parent_name = collections[collection_name]['parentCollection']
    #             friendly_name = collections[collection_name]['friendlyName']
    #             create_collection_string = f"{safe_delete_name}.create_collections(start_collection='{parent_name}', collection_names='{collection_name}', friendly_name='{friendly_name}')"
            
    #         else:
    #             collection_name = self._return_real_collection_name(name)
    #             parent_name = collections[collection_name]['parentCollection']
    #             friendly_name = collections[collection_name]['friendlyName']
    #             create_collection_string = f"create_collections(start_collection='{parent_name}', collection_names='{collection_name}', friendly_name='{friendly_name}')"
    #             create_colls_list.append(create_collection_string)
        
    #     print("Copy and run the below code in your program to recreate the collection/collections:", '\n')
    #     if len(collection_names) == 1:
    #         print(create_collection_string)
    #     else:
    #         for item in create_colls_list:
    #             create_coll_final_string = f"{safe_delete_name}.{item}"
    #             print(create_coll_final_string)
    #     print('\n')
    #     print('end of code')
    #     print('\n')

            


        # create_colls_list = []
        # for name in collection_names:
        #     if len(collection_names) == 1:
        #         collection_name = self._return_real_collection_name(name)
        #         parent_name = collections[collection_name]['parentCollection']
        #         create_collection_string = f"{safe_delete_name}.create_collections('{parent_name}', ['{name}'])"
            
        #     else:
        #         collection_name = self._return_real_collection_name(name)
        #         parent_name = collections[collection_name]['parentCollection']
        #         create_collection_string = f"create_collections('{parent_name}', ['{name}'])"
        #         create_colls_list.append(create_collection_string)
        
        # print("Copy and run the below code in your program to recreate the collections:", '\n')
        # if len(collection_names) == 1:
        #     print(create_collection_string)
        # else:
        #     for item in create_colls_list:
        #         create_coll_final_string = f"{safe_delete_name}.{item}"
        #         print(create_coll_final_string)
        # print('\n')
        # print('end of code')
        # print('\n')


        # delete_list = []
        # recursive_list = []

        # for name in collection_names:
        #     name = self._return_real_collection_name(name)
        #     self._recursive_append(name, delete_list)
        #     if delete_list[0] is not None:
        #         for item in delete_list:
        #                 self._recursive_append(item, recursive_list)
        #         for item2 in recursive_list:
        #             if item2 is not None:
        #                 delete_list.append(item2)
        #                 self._recursive_append(item2, recursive_list)
        
        # if delete_list[0] is not None:
        #     if also_delete_first_collection:
        #         delete_list.insert(0, collection_names[0])
        #     # for coll in delete_list[::-1]: # starting from the most child collection
        #     #     self.delete_collections([coll])


        # if recursive_list[0] is None:
        #     create_collection_string = f"{safe_delete}.create_collections('{parent_name}', ['{name}'])"
        #     print(create_collection_string)



















    def test2(self): # request Session was either same time or even slower for larger operations
        import json
        names = ['test' + str(i) for i in range(260,320)]
       
        for name in names:
            url = f'https://{self.purview_account_name}.purview.azure.com/account/collections/{name}?api-version=2019-11-01-preview'
            data = f'{{"parentCollection": {{"referenceName": "nblple"}}, "friendlyName": "{name}"}}'

            # s = requests.Session()

            coll_request = coll_request = requests.put(url=url, headers=self.header, data=data)
            print(coll_request.content)


        # s.close()

            # with requests.Session() as s:
            #     coll_request = s.put(url=url, headers=self.header, data=data)
            #     print(coll_request.content)
        
        # coll_request = requests.put(url=url, headers=self.header, data=json.dumps(data))
        # print(coll_request.content)



    # def delete_collections(self, collection_names: list[str], force_actual_name: bool = False, api_version: str = None):
    #     """ Can delete one or more collections. Can pass in either the actual or friendly collection name."""

    #     if not api_version:
    #         api_version = self.collections_api_version
    #     for name in collection_names:
    #         coll_name = self._return_real_collection_name(name, force_actual_name)   
    #         url = f"{self.collections_endpoint}/{coll_name}?api-version={api_version}"
    #         try:
    #             delete_collections_request = requests.delete(url=url, headers=self.header)
    #             if not delete_collections_request.content:
    #                 print(f"The collection '{name}' was successfully deleted")
    #             else:
    #                 print(delete_collections_request.content)
    #         except Exception as e:
    #             raise e


    # def create_collections2(self, start_collection: str, collection_names: list[str], force_actual_name: bool = False, api_version: str = None): 
    #     """
    #     Create a collection or several collections in Purview. Can do any of following:
    #         -Create one collection
    #         -Create multiple collections
    #         -Create one collection hierarchy (multiple parent child relationships)
    #         -Create multiple collection hierarchies
        
    #     :param start_collection: String. Existing collection name to start creating the collections from. 
    #             Can either pass in the actual Purview collection name or the friendly collection name.
    #             If you pass in the friendly name and duplicate friendly names exist, you'll receive a friendly error
    #             asking which collection you'd like to use. This collection has to exist already in Purview.  
    #     :param collection_names: List of Strings list[str]. As mentioned above, you can pass in as many as needed.
    #             examples:
    #             -One collection: pur.create_collections('startcollname', ['mynewcollection'])
    #             -Multiple collections: pur.create_collections('startcollname', ['mynewcollection', 'mynewcollectiontwo'])
    #             -Create one collection hierarchy: pur.create_collections('startcollname', ['mynewcollection/mysubcoll1/mysubcoll2'])
    #                 The / is the parent child relationship. mysubcoll1 would be a child of mynewcollection. 
    #                 mysubcoll2 would be a child of mysubcoll1.
    #             -Create multiple collection hierarchies: pur.create('startcollname', ['mynewcollection/mysubcoll1', 'mysecondcollection/mysubcoll2'])
    #                 The internal code will handle any Purview name requirements. my new collection is a valid name to pass in.
    #     :param force_actual_name: String. Edge Case. If a friendly name is passed in the start_collection parameter 
    #             and that name is duplicated across multiple hierarchies and one of those names is the actual passed in name, if True, this will force
    #             the method to use the actual name you pass in if it finds it.
    #             examples:
    #             -If startcollname is passed in the start_collection parameter and that name exists under multiple hierarchies (friendly names)
    #             if one of the actual names (not friendly name) is startcollname, then it will force the code to use the startcollname. 
    #     :param api_version (optional): String. Default is None. If None, it uses the self.collections_api_version which is "2019-11-01-preview".
    #     :return: None
    #     :rtype None
    #     """

    #     if not api_version:
    #         api_version = self.collections_api_version
        
    #     coll_dict = self.list_collections(only_names=True, api_version=api_version)
    #     start_collection = self._return_real_collection_name(start_collection, api_version, force_actual_name)
    
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
    #         updated_collection_list = self._return_updated_collection_list(start_collection, colls, coll_dict, api_version)
    #         for index, name in enumerate(updated_collection_list):
    #             if index == 0:
    #                 if name in coll_dict and coll_dict[name]['parentCollection'].lower() == start_collection.lower():
    #                     continue
    #                 else:
    #                     friendly_name = colls[index]

    #                 try:
    #                     request = self._return_request_info2(name=name, friendly_name=friendly_name, parent_collection=start_collection, api_version=api_version)
    #                     print(request.content)
    #                     print('\n')
    #                 except Exception as e:
    #                     raise e

    #             else:
    #                 if name in coll_dict and coll_dict[name]['parentCollection'].lower() == updated_collection_list[index - 1].lower():
    #                     continue
                      
    #                 else:
    #                     friendly_name = colls[index]
    #                     parent_collection = updated_collection_list[index - 1]
                
    #                 try:

    #                     request = self._return_request_info2(name=name, friendly_name=friendly_name, parent_collection=parent_collection, api_version=api_version)
    #                     print(request.content)
    #                     print('\n')
    #                 except Exception as e:
    #                     raise e




    # def _return_request_info2(self, name, friendly_name, parent_collection, api_version):
    #     """
    #     Internal helper function. Do not call directly.
    #     """
    #     with requests.Session() as s:

    #         url = f'{self.collections_endpoint}/{name}?api-version={api_version}'
    #         data = f'{{"parentCollection": {{"referenceName": "{parent_collection}"}}, "friendlyName": "{friendly_name}"}}'
    #         request = s.put(url=url, headers=self.header, data=data)
        
    #         return request