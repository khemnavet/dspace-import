from enum import Enum

class DSOTypes(Enum):
    COMMUNITY = 1
    COLLECTION = 2

class DSO(object):
    def __init__(self, uuid, name, parent, type, itemsLoaded=False):
        self.id = id(self)
        self.uuid = uuid
        self.name = name
        self.parent = parent
        self.type = type
        self.itemsLoaded = itemsLoaded
        self.children = []
        self.collections = []

    def addChild(self, childId):
        self.children.append(childId)

    def addCollection(self, collId):
        self.collections.append(collId)

    def isCommunity(self):
        return self.type == DSOTypes.COMMUNITY

    def isCollection(self):
        return self.type == DSOTypes.COLLECTION
    
#############################################################################################################################################    

class ImporterData:
    """ shared data to be used by importer application """
    # a singleton
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    # may have to add self.lock = Threading.lock to __init__
    # method that wants to use a shared variable use with self.lock to acquire a lock for the variable then modify/read the variable
    def __init__(self) -> None:
        self.__communities_collections = {}

    # getters
    @property
    def communities_and_collections(self):
        return self.__communities_collections

    def add_community_and_collections(self, community_uuid, community: DSO):
        self.__communities_collections[community_uuid] = community