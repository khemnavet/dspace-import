from dspacecommunityrequest import DspaceCommunityRequest
from config import ImporterConfig
from dataobjects import ImporterData, DSO, DSOTypes
from dspaceauthservice import DspaceAuthService
from requests import HTTPError

class CommunityException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class CommunityService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, shared_data: ImporterData) -> None:
        auth_service = DspaceAuthService(config)
        self.__shared_data = shared_data
        self.__community_request = DspaceCommunityRequest(config.dspace_rest_url(), auth_service.get_bearer_jwt(), auth_service.get_auth_cookies())
    
    def get_top_communities(self):
        try:
            comms = self.__community_request.top_communities()
            if comms["page"]["totalElements"] > 0:
                for community in comms["_embedded"]["communities"]:
                    dsObject = DSO(community["uuid"], community["name"], None, DSOTypes.COMMUNITY)
                    self.__shared_data.add_community_and_collections(dsObject)
                    self.__shared_data.add_top_community(dsObject.id)
        except HTTPError as err:
            print(f"Exception when getting top communities. Error code {err.response.status_code}, reason {err.response.reason}")
            raise CommunityException(err.response.reason)
        
    def get_subcommunities(self, community: DSO):
        result = []
        if community is None:
            # return top communities
            print("return top communities")
            for c_id in self.__shared_data.top_communities:
                result.append(self.__shared_data.communities_and_collections[c_id])
        else:
            # may have sub communities cached
            print("return cached sub communities")
            comm_dso = self.__shared_data.communities_and_collections[community.id]
            if comm_dso.itemsLoaded and len(comm_dso.children) > 0:
                # have sub communities to return
                for c_id in comm_dso.children:
                    result.append(self.__shared_data.communities_and_collections[c_id])
            elif not comm_dso.itemsLoaded:
                # request these from server
                print("get sub communities from server")
                try:
                    comms = self.__community_request.sub_communities(comm_dso.uuid)
                    if comms["page"]["totalElements"] > 0:
                        for sub_comm in comms["_embedded"]["subcommunities"]:
                            dsObject = DSO(sub_comm["uuid"], sub_comm["name"], comm_dso.id, DSOTypes.COMMUNITY)
                            self.__shared_data.add_community_and_collections(dsObject)
                            comm_dso.addChild(dsObject.id)
                            result.append(dsObject)
                    comm_dso.itemsLoaded = True
                except HTTPError as err:
                    print(f"Exception getting sub communities for {community.name}. Error code {err.response.status_code}, reason {err.response.reason}")
                    raise CommunityException(err.response.reason)
                
            return result