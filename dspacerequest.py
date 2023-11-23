import requests
from pathlib import Path
import mimetypes

class PublicDspaceRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL):
        self.__dspaceRestURL = dspaceRestURL

    def get_metadata_schemas(self):
        try:
            # print("get metadata schemas")
            req = requests.get(self.__dspaceRestURL + "/api/core/metadataschemas", headers={"Accept":"application/json"})
            if req.status_code == requests.codes.ok:
                #print(req.text)
                return req.json()
            req.raise_for_status()
        except:
            raise
    
    def get_metadata_schema_fields(self, prefix, page):
        try:
            # print(f"get metadata fields for {prefix}")
            req = requests.get(self.__dspaceRestURL + "/api/core/metadatafields/search/bySchema", params={"schema": prefix, "page": page}, headers={"Accept": "application/json"})
            if req.status_code == requests.codes.ok:
                return req.json()
            req.raise_for_status()
        except:
            raise

class DspaceCommunityRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL: str, jwt, cookie) -> None:
        self.__dspaceRestURL = dspaceRestURL
        self.__bearer_jwt = jwt
        self.__cookie = cookie

    def top_communities(self): #return json
        req = requests.get(self.__dspaceRestURL + "/api/core/communities/search/top", headers={"Accept":"application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()

    def sub_communities(self, community_uuid, page_number = 0):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/communities/{community_uuid}/subcommunities?page={page_number}", headers={"Accept":"application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()
    
    def sub_collections(self, community_uuid, page_number = 0):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/communities/{community_uuid}/collections?page={page_number}", headers={"Accept":"application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()

class DspaceItemRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL: str, jwt, cookie, csrf_token):
        self.__dspaceRestURL = dspaceRestURL
        self.__bearer_jwt = jwt
        self.__cookie = cookie
        self.__csrf_token = csrf_token

    def get_item(self, item_uuid):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}", headers={"Accept": "application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()
    
    def item_owning_collection(self, item_uuid):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/owningCollection", headers={"Accept":"application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()

    def item_bundles(self, item_uuid):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/bundles", headers={"Accept": "application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()
    
    def new_item(self, item_json, owning_collection_uuid):
        req = requests.post(f"{self.__dspaceRestURL}/api/core/items?owningCollection={owning_collection_uuid}", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}, cookies=self.__cookie, data=item_json)
        if req.status_code == requests.codes.created:
            return req.json()
        req.raise_for_status()

class DspaceBundleRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL: str, jwt, cookie, csrf_token) -> None:
        self.__dspaceRestURL = dspaceRestURL
        self.__bearer_jwt = jwt
        self.__cookie = cookie
        self.__csrf_token = csrf_token
    
    def has_primary_bitstream(self, bundle_uuid) -> bool:
        req = requests.get(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", headers={"Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        return req.status_code == requests.codes.ok
    
    def delete_primary_bitstream_flag(self, bundle_uuid):
        req = requests.delete(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token}, cookies=self.__cookie)
        if req.status_code == requests.codes.no_content:
            return True
        req.raise_for_status()
    
    def get_bitstreams(self, bundle_uuid, page):
        req = requests.get(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/bitstreams?page={page}", headers={"Accept": "application/json", "Authorization": self.__bearer_jwt}, cookies=self.__cookie)
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()
    
    def new_bundle(self, bundle_json, item_uuid):
        req = requests.post(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/bundles", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token, "Content-Type": "application/json", "Accept": "application/json"}, cookies=self.__cookie, data=bundle_json)
        if req.status_code == requests.codes.created:
            return req.json()
        req.raise_for_status()
    
    def add_primary_bitstream(self, bundle_uuid, bitstream_uuid):
        req = requests.post(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token, "Content-Type": "text/uri-list"}, cookies=self.__cookie, data=f"{self.__dspaceRestURL}/api/core/bitstreams/{bitstream_uuid}")
        if req.status_code == requests.codes.created:
            return True
        req.raise_for_status()

class DspaceBitstreamRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, dspaceRestURL: str, jwt, cookie, csrf_token) -> None:
        self.__dspaceRestURL = dspaceRestURL
        self.__bearer_jwt = jwt
        self.__cookie = cookie
        self.__csrf_token = csrf_token

    def delete_bitstream(self, bitstream_uuid):
        req = requests.delete(f"{self.__dspaceRestURL}/api/core/bitstreams/{bitstream_uuid}", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token}, cookies=self.__cookie)
        if req.status_code == requests.codes.no_content:
            return True
        req.raise_for_status()

    def new_bitstream(self, bundle_uuid, file: Path):
        files = [('file', (file.name, open(file, "rb"), mimetypes.types_map[file.suffix.lower()]))]
        req = requests.post(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/bitstreams", headers={"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token}, data={}, files=files)
        if req.status_code == requests.codes.created:
            return req.json()
        req.raise_for_status()