from enum import Enum, auto
from json import dumps
from typing import Any
import base64
import json

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

class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return name
    
class BundleType(AutoName):
    ORIGINAL = auto()
    THUMBNAIL = auto()

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
        self.__remove_extra_metadata = ""
        self.__metadata_to_match = ""
        self.__item_directory = ""
        self.__file_name_column = ""
        self.__match_file_name = ItemFileMatchType.EXACT
        self.__file_name_extension = ""
        self.__remove_existing_files = YesNo.NO
        self.__primary_bitstream_column = ""
        self.__metadata_schemas = {}

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
    def remove_extra_metadata(self) -> bool:
        return self.__remove_extra_metadata == YesNo.YES
    
    @property
    def metadata_to_match(self) -> bool:
        return self.__metadata_to_match == YesNo.YES
    
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
    
    @property
    def primary_bitstream_column(self):
        return self.__primary_bitstream_column

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
    
    @remove_extra_metadata.setter
    def remove_extra_metadata(self, extra: YesNo):
        self.__remove_extra_metadata = extra
    
    @metadata_to_match.setter
    def metadata_to_match(self, to_match: YesNo):
        self.__metadata_to_match = to_match
    
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
    
    @primary_bitstream_column.setter
    def primary_bitstream_column(self, col_name):
        self.__primary_bitstream_column = col_name
    
    def set_metadata_schemas(self, schemas):
        self.__metadata_schemas = schemas
    
    def get_schemas(self) -> list:
        return list(self.__metadata_schemas)
    
    def get_schema_fields(self, prefix) -> list:
        fields = []
        for name in self.__metadata_schemas[prefix].exact_name():
            fields.append(name)
        return fields

#############################################################################################################################################

class AuthData:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self) -> None:
        self.__jwt = ''
        self.__cookie_jar = None
        self.__CSRF_token = ''
        self.__jwt_decoded = {"header": "", "payload":"", "signature":""}
        self.__username = ''
    
    def __b64_padding(self, token_len) -> str:
        return '='*(4 - (token_len % 4))

    @property
    def bearer_jwt(self):
        return "Bearer " + self.__jwt
    
    @property
    def csrf_token(self):
        return self.__CSRF_token
    
    @property
    def auth_cookie(self):
        return self.__cookie_jar
    
    @property
    def username(self):
        return self.__username
    
    @bearer_jwt.setter
    def bearer_jwt(self, token):
        self.__jwt = token
        token_comps = self.__jwt.split(".")
        self.__jwt_decoded["header"] = json.loads(base64.urlsafe_b64decode(token_comps[0]).decode(encoding="utf-8"))
        self.__jwt_decoded["signature"] = token_comps[2]
        self.__jwt_decoded["payload"] = json.loads(base64.urlsafe_b64decode(f"{token_comps[1]}{self.__b64_padding(len(token_comps[1]))}").decode(encoding="utf-8"))
    
    @csrf_token.setter
    def csrf_token(self, token):
        self.__CSRF_token = token
    
    @auth_cookie.setter
    def auth_cookie(self, cookie):
        self.__cookie_jar = cookie
    
    @username.setter
    def username(self, user):
        self.__username = user
    

#############################################################################################################################################

class Item:
    def __init__(self, item_id = "", uuid = "", name = "", handle = "", metadata = {}, existing_metadata = {}, in_archive = True, discoverable = True, withdrawn = True) -> None:
        self.__item_id = item_id
        self.__uuid = uuid
        self.__name = name
        self.__handle = handle
        self.__metadata = metadata
        self.__existing_metadata = existing_metadata
        self.__inArchive = in_archive
        self.__discoverable = discoverable
        self.__withdrawn = withdrawn
        self.__type = "item"

    @property
    def item_id(self):
        return self.__item_id
    
    @property
    def uuid(self):
        return self.__uuid
    
    @property
    def name(self):
        return self.__name

    @property
    def handle(self):
        return self.__handle
    
    @property
    def metadata(self):
        return self.__metadata
    
    @property
    def existing_metadata(self):
        return self.__existing_metadata
    
    @property
    def inArchive(self):
        return self.__inArchive

    @property
    def discoverable(self):
        return self.__discoverable
    
    @property
    def withdrawn(self):
        return self.__withdrawn
    
    @item_id.setter
    def item_id(self, itemid):
        self.__item_id = itemid
    
    @uuid.setter
    def uuid(self, item_uuid):
        self.__uuid = item_uuid
    
    @name.setter
    def name(self, item_name):
        self.__name = item_name
    
    @handle.setter
    def handle(self, item_handle):
        self.__handle = item_handle

    @metadata.setter
    def metadata(self, item_metadata: dict):
        self.__metadata = item_metadata
    
    @existing_metadata.setter
    def existing_metadata(self, item_metadata: dict):
        self.__existing_metadata = item_metadata
    
    @inArchive.setter
    def inArchive(self, in_archive):
        self.__inArchive = in_archive
    
    @discoverable.setter
    def discoverable(self, item_discoverable):
        self.__discoverable = item_discoverable
    
    @withdrawn.setter
    def withdrawn(self, item_withdrawn):
        self.__withdrawn = item_withdrawn
    
    def set_patch_operations(self, remove_extra_metadata: bool, metadata_to_match: bool, metadata_not_to_remove: list):
        patch_ops = []
        existing_keys = {key for key in self.__existing_metadata.keys() if key not in metadata_not_to_remove}
        excel_keys = self.__metadata.keys()
        #print(f"existing keys: {existing_keys}")
        #print(f"excel keys: {excel_keys}")

        #print("fields in excel file but not on database")
        for metadata_field in excel_keys - existing_keys: # in excel but not on database:
            #print(f"op - add, field: {metadata_field}, value: {self.__metadata[metadata_field]}")
            for metadata_value in self.__metadata[metadata_field]:
                patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": metadata_value})

        if metadata_to_match:
            if remove_extra_metadata:
                #print("metadata to match and remove extra metadata")
                for metadata_field in existing_keys - excel_keys: # on database but not in excel
                    patch_ops.append({"op": "remove", "path": "/metadata/"+metadata_field})
        
            for metadata_field in existing_keys & excel_keys: # intersection - same metadata fields
                #remove the field and add with new value(s)
                patch_ops.append({"op": "remove", "path": "/metadata/"+metadata_field})
                for i in range(len(self.__metadata[metadata_field])):
                    patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": self.__metadata[metadata_field][i]})
        
        else:
            #print("metadata fields common between database and excel")
            for metadata_field in existing_keys & excel_keys: # intersection - same metadata fields
                for i in range(len(self.__metadata[metadata_field])):
                    #print(f"add metadata, field: {metadata_field}, position: {last_position}, value: {self.__metadata[metadata_field][i]}")
                    patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": self.__metadata[metadata_field][i]})
        
        #print(patch_ops)
        self.__patch_operations = patch_ops

    def to_json_str(self) -> str:
        item_json = {}
        if len(self.__item_id) > 0:
            item_json["id:"] = self.__item_id
        if len(self.__uuid) > 0:
            item_json["name"] = self.__uuid
        item_json["name"] = self.__name
        if len(self.__handle) > 0:
            item_json["handle"] = self.__handle
        item_json["metadata"] = self.__metadata
        item_json["inArchive"] = self.__inArchive
        item_json["discoverable"] = self.__discoverable
        item_json["withdrawn"] = self.__withdrawn
        item_json["type"] = self.__type

        return dumps(item_json)

    def to_patch_str(self) -> str:
        return dumps(self.__patch_operations)

#############################################################################################################################################

class Bundle:
    def __init__(self, bundle_type: BundleType, uuid = "") -> None:
        self.__uuid = uuid
        self.__name = bundle_type.name
    
    @property
    def uuid(self):
        return self.__uuid

    @property
    def name(self):
        return self.__name
    
    @uuid.setter
    def uuid(self, bundle_uuid):
        self.__uuid = bundle_uuid
    
    @name.setter
    def name(self, bundle_name: BundleType):
        self.__name = bundle_name.name
    
    def to_json_str(self) -> str:
        return dumps({"name": self.__name, "metadata": {}})

#############################################################################################################################################

class Bitstream:
    def __init__(self, bitstream_id = "", uuid = "", name = "") -> None:
        self.__id = bitstream_id
        self.__uuid = uuid
        self.__name = name
        self.__type = "bitstream"
    
    @property
    def bitstream_id(self):
        return self.__id

    @property
    def uuid(self):
        return self.__uuid

    @property
    def name(self):
        return self.__name
    
    @bitstream_id.setter
    def bitstream_id(self, new_id):
        self.__id = new_id
    
    @uuid.setter
    def uuid(self, new_uuid):
        self.__uuid = new_uuid
    
    @name.setter
    def name(self, new_name):
        self.__name = new_name