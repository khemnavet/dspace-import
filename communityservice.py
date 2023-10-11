from dspacecommunityrequest import DspaceCommunityRequest
from config import ImporterConfig
from dataobjects import ImporterData, DSO, DSOTypes
from requests import HTTPError

class CommunityException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class CommunityService:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, shared_data: ImporterData) -> None:
        self.__shared_data = shared_data
        self.__community_request = DspaceCommunityRequest(config.dspace_rest_url(), shared_data.cookie_and_jwt())
    
    def get_top_communities(self):
        try:
            comms = self.__community_request.top_communities()
            if comms["page"]["totalElements"] > 0:
                for community in comms["_embedded"]["communities"]:
                    dsObject = DSO(community["uuid"], community["name"], None, DSOTypes.COMMUNITY)
                    self.__shared_data.add_community_and_collections(community["uuid"], dsObject)
        except HTTPError as err:
            print(f"Exception when getting top communities. Error code {err.response.status_code}, reason {err.response.reason}")
            raise CommunityException(err.response.reason)