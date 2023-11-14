from enum import Enum

class DSOTypes(Enum):
    COMMUNITY = 1
    COLLECTION = 2

class YesNo(Enum):
    YES = 1
    NO = 2

class FileBrowseType(Enum):
    FILE = 1
    DIR = 2

class ItemFileMatchType(Enum):
    EXACT = 1
    BEGINS = 2

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
        self.__selected_collection = None
        self.__item_file = ""
        self.__item_file_sheet = ""
        self.__title_column = ""
        self.__column_mapping = {}
        self.__item_uuid_column = ""
        self.__update_existing = ""
        self.__item_directory = ""
        self.__file_name_column = ""
        self.__match_file_name = ItemFileMatchType.EXACT
        self.__file_name_extension = ""
        self.__remove_existing_files = YesNo.NO

    # getters
    @property
    def selected_collection(self) -> DSO:
        return self.__selected_collection
    
    @property
    def item_file(self):
        return self.__item_file
    
    @property
    def item_file_sheet(self):
        return self.__item_file_sheet

    @property
    def title_column(self):
        return self.__title_column
    
    @property
    def column_mapping(self):
        return self.__column_mapping
    
    @property
    def item_uuid_column(self):
        return self.__item_uuid_column
    
    @property
    def update_existing(self) -> bool:
        return self.__update_existing == YesNo.YES
    
    @property
    def item_directory(self):
        return self.__item_directory

    @property
    def file_name_column(self):
        return self.__file_name_column

    @property
    def file_name_matching(self):
        return self.__match_file_name
    
    @property
    def file_extension(self):
        return self.__file_name_extension

    @property
    def remove_existing_files(self) -> bool:
        return self.__remove_existing_files == YesNo.YES

    @selected_collection.setter
    def selected_collection(self, coll: DSO):
        self.__selected_collection = coll
    
    @item_file.setter
    def item_file(self, file_name):
        self.__item_file = file_name
    
    @item_file_sheet.setter
    def item_file_sheet(self, sheet_name):
        self.__item_file_sheet = sheet_name
    
    @title_column.setter
    def title_column(self, title):
        self.__title_column = title
    
    @column_mapping.setter
    def column_mapping(self, mapping: dict):
        self.__column_mapping = mapping

    @item_uuid_column.setter
    def item_uuid_column(self, dup):
        self.__item_uuid_column = dup
    
    @update_existing.setter
    def update_existing(self, existing: YesNo):
        self.__update_existing = existing
    
    @item_directory.setter
    def item_directory(self, dir):
        self.__item_directory = dir

    @file_name_column.setter
    def file_name_column(self, col_name):
        self.__file_name_column = col_name
    
    @file_name_matching.setter
    def file_name_matching(self, match: ItemFileMatchType):
        self.__match_file_name = match
    
    @file_extension.setter
    def file_extension(self, ext:str):
        self.__file_name_extension = "."+ext.strip().lstrip(".") if len(ext.strip()) > 0 else ""
    
    @remove_existing_files.setter
    def remove_existing_files(self, rem: YesNo):
        self.__remove_existing_files = rem