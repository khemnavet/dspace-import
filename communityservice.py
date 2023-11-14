from dspacerequest import DspaceCommunityRequest
from config import ImporterConfig
from dataobjects import DSO, DSOTypes
from dspaceauthservice import DspaceAuthService
from requests import HTTPError

class CommunityException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class CommunityService:
    _self = None
    _top_communities = []
    _communities_collections = {}

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig) -> None:
        auth_service = DspaceAuthService(config)
        self.__community_request = DspaceCommunityRequest(config.dspace_rest_url(), auth_service.get_bearer_jwt(), auth_service.get_auth_cookies())
    
    def __add_community_and_collections(self, community: DSO):
        self._communities_collections[community.id] = community

    def __add_top_community(self, community_id):
        self._top_communities.append(community_id)

    # getters
    @property
    def communities_and_collections(self):
        return self._communities_collections
    
    @property
    def top_communities(self):
        return self._top_communities

    def get_top_communities(self):
        try:
            comms = self.__community_request.top_communities()
            if comms["page"]["totalElements"] > 0:
                for community in comms["_embedded"]["communities"]:
                    dsObject = DSO(community["uuid"], community["name"], None, DSOTypes.COMMUNITY)
                    self.__add_community_and_collections(dsObject)
                    self.__add_top_community(dsObject.id)
        except HTTPError as err:
            print(f"Exception when getting top communities. Error code {err.response.status_code}, reason {err.response.reason}")
            raise CommunityException(err.response.reason)
        
    def get_subcommunities(self, community: DSO):
        result = []
        if community is None:
            # return top communities
            print("return top communities")
            for c_id in self._top_communities:
                result.append(self._communities_collections[c_id])
        else:
            # may have sub communities cached
            comm_dso = self._communities_collections[community.id]
            if comm_dso.itemsLoaded:
                print("return cached sub communities")
                # have sub communities to return
                for c_id in comm_dso.children:
                    result.append(self._communities_collections[c_id])
            else:
                # request these from server
                print("get sub communities from server")
                try:
                    curr_page = 0
                    total_pages = 1
                    while curr_page < total_pages:
                        comms = self.__community_request.sub_communities(comm_dso.uuid, curr_page)
                        total_pages = comms["page"]["totalPages"]
                        for sub_comm in comms["_embedded"]["subcommunities"]:
                            #print(f"page {curr_page}")
                            dsObject = DSO(sub_comm["uuid"], sub_comm["name"], comm_dso.id, DSOTypes.COMMUNITY)
                            self.__add_community_and_collections(dsObject)
                            comm_dso.addChild(dsObject.id)
                            result.append(dsObject)

                        curr_page = curr_page + 1

                    comm_dso.itemsLoaded = True
                except HTTPError as err:
                    print(f"Exception getting sub communities for {community.name}. Error code {err.response.status_code}, reason {err.response.reason}")
                    raise CommunityException(err.response.reason)
                
        return result
        
    def get_community_dso(self, community_id):
        return self._communities_collections[community_id]
    
    def get_collections(self, community: DSO):
        result = []
        comm_dso = self._communities_collections[community.id]
        if comm_dso.collectionsLoaded:
            # return cached collections
            print("return cached collections")
            for c_id in comm_dso.collections:
                result.append(self._communities_collections[c_id])
        else:
            # get the collections from the server
            print("get collections from server")
            try:
                curr_page = 0
                total_pages = 1
                while curr_page < total_pages:
                    colls = self.__community_request.sub_collections(comm_dso.uuid, curr_page)
                    total_pages =  colls["page"]["totalPages"]
                    for coll in colls["_embedded"]["collections"]:
                        dsObject = DSO(coll["uuid"], coll["name"], comm_dso.id, DSOTypes.COLLECTION)
                        self.__add_community_and_collections(dsObject)
                        comm_dso.addCollection(dsObject.id)
                        result.append(dsObject)

                    curr_page = curr_page + 1
                    
                comm_dso.collectionsLoaded = True
            except HTTPError as err:
                print(f"Exception getting collections for {community.name}. Error code {err.response.status_code}, reason {err.response.reason}")
                raise CommunityException(err.response.reason)
        return result
