import requests
from pathlib import Path
import mimetypes

class DspaceRequest:

    def __ok_response(req: requests.Response):
        if req.status_code == requests.codes.ok:
            return req.json()
        req.raise_for_status()

    def dspace_get_no_cookie(self, url, req_headers):
        return self.__ok_response(requests.get(url, headers=req_headers))
        
    def dspace_get(self, url, req_headers, req_cookies):
        return self.__ok_response(requests.get(url, headers=req_headers, cookies=req_cookies))
    
    def dspace_create_post(self, url, req_headers, req_cookies, req_data):
        req = requests.post(url, headers=req_headers, cookies=req_cookies, data=req_data)
        if req.status_code == requests.codes.created:
            return req.json()
        req.raise_for_status()



class PublicDspaceRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL):
        self.__dspaceRestURL = dspaceRestURL

    def get_metadata_schemas(self):
        return self.dspace_get_no_cookie(f"{self.__dspaceRestURL}/api/core/metadataschemas", {"Accept":"application/json"})
    
    def get_metadata_schema_fields(self, prefix, page):
        return self.dspace_get_no_cookie(f"{self.__dspaceRestURL}/api/core/metadatafields/search/bySchema?schema={prefix}&page={page}", {"Accept": "application/json"})

class DspaceCommunityRequest(DspaceRequest):
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
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/communities/search/top", {"Accept":"application/json", "Authorization": self.__bearer_jwt}, self.__cookie)

    def sub_communities(self, community_uuid, page_number = 0):
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/communities/{community_uuid}/subcommunities?page={page_number}", {"Accept":"application/json", "Authorization": self.__bearer_jwt}, self.__cookie)
    
    def sub_collections(self, community_uuid, page_number = 0):
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/communities/{community_uuid}/collections?page={page_number}", {"Accept":"application/json", "Authorization": self.__bearer_jwt}, self.__cookie)

class DspaceItemRequest(DspaceRequest):
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
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}", {"Accept": "application/json", "Authorization": self.__bearer_jwt}, self.__cookie)
    
    def item_owning_collection(self, item_uuid):
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/owningCollection", {"Accept":"application/json", "Authorization": self.__bearer_jwt}, self.__cookie)

    def item_bundles(self, item_uuid):
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/bundles", {"Accept": "application/json", "Authorization": self.__bearer_jwt}, self.__cookie)
    
    def new_item(self, item_json, owning_collection_uuid):
        return self.dspace_create_post(f"{self.__dspaceRestURL}/api/core/items?owningCollection={owning_collection_uuid}", {"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}, self.__cookie, item_json)

class DspaceBundleRequest(DspaceRequest):
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
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", {"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token}, self.__cookie)
    
    def get_bitstreams(self, bundle_uuid, page):
        return self.dspace_get(f"{self.__dspaceRestURL}/api/core/bundles/{bundle_uuid}/bitstreams?page={page}", {"Accept": "application/json", "Authorization": self.__bearer_jwt}, self.__cookie)
    
    def new_bundle(self, bundle_json, item_uuid):
        return self.dspace_create_post(f"{self.__dspaceRestURL}/api/core/items/{item_uuid}/bundles", {"Authorization": self.__bearer_jwt, "X-XSRF-TOKEN": self.__csrf_token, "Content-Type": "application/json", "Accept": "application/json"}, self.__cookie, bundle_json)
    
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