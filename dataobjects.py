from enum import Enum

class DSOTypes(Enum):
    COMMUNITY = 1
    COLLECTION = 2

class DSO(object):
    def __init__(self, uuid, name, parent, type, itemsLoaded=False, collLoaded=False):
        self.id = id(self)
        self.uuid = uuid
        self.name = name
        self.parent = parent
        self.type = type
        self.itemsLoaded = itemsLoaded # if sub-communities have been obtained from the server for this community
        self.collectionsLoaded = collLoaded # if the collections have been obtained from the server for this community
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
        self.__selected_community = None
        self.__title_column = ""
        self.__column_mapping = {}
        self.__duplicate_column = ""
        self.__update_existing = ""

    # getters
    @property
    def selected_community(self) -> DSO:
        return self.__selected_community

    @property
    def title_column(self):
        return self.__title_column
    
    @property
    def column_mapping(self):
        return self.__column_mapping
    
    @property
    def duplicate_column(self):
        return self.__duplicate_column
    
    @property
    def update_existing(self):
        return self.__update_existing

    @selected_community.setter
    def selected_community(self, coll: DSO):
        self.__selected_community = coll
    
    @title_column.setter
    def title_column(self, title):
        self.__title_column = title
    
    @column_mapping.setter
    def column_mapping(self, mapping: dict):
        self.__column_mapping = mapping

    @duplicate_column.setter
    def duplicate_column(self, dup):
        self.__duplicate_column = dup
    
    @update_existing.setter
    def update_existing(self, existing):
        self.__update_existing = existing