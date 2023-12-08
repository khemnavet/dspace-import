from dataobjects import AuthData
import requests
from pathlib import Path
import mimetypes

class DspaceRequest:

    def __init__(self, authData: AuthData, dspaceRestURL) -> None:
        self.authData = authData
        self.dspaceRestURL = dspaceRestURL

    def auth_status(self):
        auth_req = requests.get(self.dspaceRestURL + "/api/authn/status", headers={"Accept":"application/json"})
        if auth_req.status_code == requests.codes.ok:
            return auth_req
        auth_req.raise_for_status()
    
    def save_auth(self):
        resp = self.auth_status()
        if "DSPACE-XSRF-TOKEN" in resp.headers:
            self.authData.csrf_token = resp.headers["DSPACE-XSRF-TOKEN"]
        if "Authorization" in resp.headers:
            self.authData.bearer_jwt = resp.headers["Authorization"].split(" ")[1]
        self.authData.auth_cookie = resp.cookies
    
    def success(self, req: requests.Response, status_code):
        if req.status_code == status_code:
            self.save_auth()
            return req.json()
        req.raise_for_status()
    
    def success_true(self, req: requests.Response, status_code):
        if req.status_code == status_code:
            self.save_auth()
            return True
        req.raise_for_status()

    def ok_response(self, req: requests.Response):
        return self.success(req, requests.codes.ok)

    def dspace_get_no_cookie(self, url, req_headers):
        return self.success(requests.get(url, headers=req_headers), requests.codes.ok)
        
    def dspace_get(self, url, req_headers, req_cookies):
        return self.success(requests.get(url, headers=req_headers, cookies=req_cookies), requests.codes.ok)
    
    def dspace_create_post(self, url, req_headers, req_cookies, req_data):
        return self.success(requests.post(url, headers=req_headers, cookies=req_cookies, data=req_data), requests.codes.created)



class PublicDspaceRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL, auth_data: AuthData):
        super().__init__(auth_data, dspaceRestURL)

    def get_metadata_schemas(self):
        return self.dspace_get_no_cookie(f"{self.dspaceRestURL}/api/core/metadataschemas", {"Accept":"application/json"})
    
    def get_metadata_schema_fields(self, prefix, page):
        return self.dspace_get_no_cookie(f"{self.dspaceRestURL}/api/core/metadatafields/search/bySchema?schema={prefix}&page={page}", {"Accept": "application/json"})

class DspaceCommunityRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self,  dspaceRestURL: str, auth_data: AuthData) -> None:
        super().__init__(auth_data, dspaceRestURL)

    def top_communities(self): #return json
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/communities/search/top", {"Accept":"application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)

    def sub_communities(self, community_uuid, page_number = 0):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/communities/{community_uuid}/subcommunities?page={page_number}", {"Accept":"application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)
    
    def sub_collections(self, community_uuid, page_number = 0):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/communities/{community_uuid}/collections?page={page_number}", {"Accept":"application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)

class DspaceItemRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL: str, auth_data: AuthData):
        super().__init__(auth_data, dspaceRestURL)

    def get_item(self, item_uuid):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/items/{item_uuid}", {"Accept": "application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)
    
    def item_owning_collection(self, item_uuid):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/items/{item_uuid}/owningCollection", {"Accept":"application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)

    def item_bundles(self, item_uuid):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/items/{item_uuid}/bundles", {"Accept": "application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)
    
    def new_item(self, item_json, owning_collection_uuid):
        return self.dspace_create_post(f"{self.dspaceRestURL}/api/core/items?owningCollection={owning_collection_uuid}", {"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}, self.authData.auth_cookie, item_json)
    
    def put_item(self, item_uuid, item_json):
        req = requests.put(f"{self.dspaceRestURL}/api/core/items/{item_uuid}", headers={"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, "Content-Type": "application/json", "Accept": "application/json"}, cookies=self.authData.auth_cookie, data=item_json)
        return self.ok_response(req)

    def patch_item(self, item_uuid, patch_json):
        req = requests.patch(f"{self.dspaceRestURL}/api/core/items/{item_uuid}", headers={"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, "Content-Type": "application/json", "Accept": "application/json"}, cookies=self.authData.auth_cookie, data=patch_json)
        return self.ok_response(req)


class DspaceBundleRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL: str, auth_data: AuthData) -> None:
        super().__init__(auth_data, dspaceRestURL)
    
    def has_primary_bitstream(self, bundle_uuid) -> bool:
        req = requests.get(f"{self.dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", headers={"Authorization": self.authData.bearer_jwt}, cookies=self.authData.auth_cookie)
        return req.status_code == requests.codes.ok
    
    def delete_primary_bitstream_flag(self, bundle_uuid):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", {"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token}, self.authData.auth_cookie)
    
    def get_bitstreams(self, bundle_uuid, page):
        return self.dspace_get(f"{self.dspaceRestURL}/api/core/bundles/{bundle_uuid}/bitstreams?page={page}", {"Accept": "application/json", "Authorization": self.authData.bearer_jwt}, self.authData.auth_cookie)
    
    def new_bundle(self, bundle_json, item_uuid):
        return self.dspace_create_post(f"{self.dspaceRestURL}/api/core/items/{item_uuid}/bundles", {"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, "Content-Type": "application/json", "Accept": "application/json"}, self.authData.auth_cookie, bundle_json)
    
    def add_primary_bitstream(self, bundle_uuid, bitstream_uuid):
        req = requests.post(f"{self.dspaceRestURL}/api/core/bundles/{bundle_uuid}/primaryBitstream", headers={"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, "Content-Type": "text/uri-list"}, cookies=self.authData.auth_cookie, data=f"{self.dspaceRestURL}/api/core/bitstreams/{bitstream_uuid}")
        return self.success_true(req, requests.codes.created)

class DspaceBitstreamRequest(DspaceRequest):
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, dspaceRestURL: str, auth_data: AuthData) -> None:
        super().__init__(auth_data, dspaceRestURL)

    def delete_bitstream(self, bitstream_uuid):
        req = requests.delete(f"{self.dspaceRestURL}/api/core/bitstreams/{bitstream_uuid}", headers={"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token}, cookies=self.authData.auth_cookie)
        return self.success_true(req, requests.codes.no_content)

    def new_bitstream(self, bundle_uuid, file: Path):
        files = [('file', (file.name, open(file, "rb"), mimetypes.types_map[file.suffix.lower()]))]
        req = requests.post(f"{self.dspaceRestURL}/api/core/bundles/{bundle_uuid}/bitstreams", headers={"Authorization": self.authData.bearer_jwt, "X-XSRF-TOKEN": self.authData.csrf_token, "Accept": "application/json"}, cookies=self.authData.auth_cookie, data={}, files=files)
        return self.success(req, requests.codes.created)