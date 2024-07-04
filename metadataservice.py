from dspacerequest import PublicDspaceRequest
from config import ImporterConfig
from metadata import MetadataSchema, MetadataField
from dataobjects import AuthData, Item
from datetime import datetime, timezone
from utils import Utils

class MetadataService:
    _self = None

    def __new__(cls, *args, **kwargs):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, auth_data: AuthData):
        self.__auth_data = auth_data
        self.__config = config
        self.__public_dspace_request = PublicDspaceRequest(config.dspace_rest_url(), auth_data)
    
    def populate_metadata_schemas(self) -> dict:
        # send request to dspace
        # throws error to be caught
        metadata_schemas = {}
        schemas = self.__public_dspace_request.get_metadata_schemas()
        # loop over schemas json, create a metadata schema, get the fields and add to metadata schema
        for schema in schemas["_embedded"]["metadataschemas"]:
            # print(schema["prefix"])
            metadata_schemas[schema["prefix"]] = MetadataSchema(schema["prefix"])
            curr_page = 0
            total_pages = 1
            # loop over the pages
            while curr_page < total_pages:
                schema_fields = self.__public_dspace_request.get_metadata_schema_fields(schema["prefix"], curr_page)
                total_pages = schema_fields["page"]["totalPages"]
                if schema_fields["page"]["totalElements"] > 0:
                    for field in schema_fields["_embedded"]["metadatafields"]:
                        # print(f"add field - {field['id']}, {field['element']}, {field['qualifier']}")
                        metadata_schemas[schema["prefix"]].add(MetadataField(field["id"], field["element"], field["qualifier"]))
                curr_page = curr_page + 1
        return metadata_schemas
    
    def provenance_metadata_value(self, template: str) -> str:
        return template.replace("{u}", self.__auth_data.username).replace("{t}", datetime.now(timezone.utc).isoformat()+" UTC")

    def item_metadata(self, row: dict, metadata_mapping: dict):
        result = {}
        for metadata_field, columns in metadata_mapping.items():
            row_metadata = []
            place = 0
            for col in columns:
                col_value = Utils.row_column_value(row, col)
                if col_value is not None:
                    row_metadata.append({"value": col_value, "language": None, "authority": None, "confidence": -1, "place": place})
                    place = place + 1
            if len(row_metadata) > 0:
                result[metadata_field] = list(row_metadata) 
        return result
    
    def item_metadata_with_provenance(self, row: dict, metadata_mapping: dict):
        result = self.item_metadata(row, metadata_mapping)
        if len(result) > 0 and self.__config.is_provenance_enabled():
            result[self.__config.provenance_metadata_field()] = [{"value": self.provenance_metadata_value(self.__config.provenance_add_value())}]
        return result
    
    def item_patch_operations(self, item: Item, remove_extra_metadata: bool, metadata_to_match: bool, metadata_not_to_remove: list):
        patch_ops = []
        existing_keys = {key for key in item.existing_metadata.keys() if key not in metadata_not_to_remove}
        new_keys = item.metadata.keys()
        #print(f"existing keys: {existing_keys}")
        #print(f"excel keys: {new_keys}")

        #print("fields in excel file but not on database")
        for metadata_field in new_keys - existing_keys: # in excel but not on database:
            #print(f"op - add, field: {metadata_field}, value: {item[metadata_field]}")
            for metadata_value in item.metadata[metadata_field]:
                patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": metadata_value})

        if metadata_to_match:
            if remove_extra_metadata:
                #print("metadata to match and remove extra metadata")
                for metadata_field in existing_keys - new_keys: # on database but not in excel
                    patch_ops.append({"op": "remove", "path": "/metadata/"+metadata_field})
        
            for metadata_field in existing_keys & new_keys: # intersection - same metadata fields
                #remove the field and add with new value(s)
                patch_ops.append({"op": "remove", "path": "/metadata/"+metadata_field})
                for i in range(len(item.metadata[metadata_field])):
                    patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": item.metadata[metadata_field][i]})
        
        else:
            #print("metadata fields common between database and excel")
            for metadata_field in existing_keys & new_keys: # intersection - same metadata fields
                for i in range(len(item.metadata[metadata_field])):
                    #print(f"add metadata, field: {metadata_field}, position: {last_position}, value: {item[metadata_field][i]}")
                    patch_ops.append({"op": "add", "path": "/metadata/"+metadata_field+"/-", "value": item.metadata[metadata_field][i]})
        
        if len(patch_ops) > 0 and self.__config.is_provenance_enabled():
            patch_ops.append({"op": "add", "path": "/metadata/"+self.__config.provenance_metadata_field()+"/-", "value": self.provenance_metadata_value(self.__config.provenance_update_value())})

        #print(patch_ops)
        return patch_ops

    def file_metadata(self, file_name: str, file_description: str) -> dict:
        metadata = {"name": file_name}
        if len(file_description) > 0:
            metadata["metadata"] = {"dc.description": [{"value": file_description, "language": None, "authority": None, "confidence": -1, "place": 0}]}
        return metadata