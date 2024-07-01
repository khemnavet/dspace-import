from dspacerequest import PublicDspaceRequest
from config import ImporterConfig
from metadata import MetadataSchema, MetadataField
from dataobjects import AuthData

class MetadataService:
    _self = None

    def __new__(cls, *args, **kwargs):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, auth_data: AuthData):
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