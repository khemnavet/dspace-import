import requests

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