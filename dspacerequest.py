import requests

class PublicDspaceRequest:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, dspaceRestURL):
        self.__dspaceRestURL = dspaceRestURL

    def get_metadata_schemas(self):
        try:
            # print("get metadata schemas")
            req = requests.get(self.__dspaceRestURL + "/api/core/metadataschemas", headers={"Accept":"application/json"})
            if req.status_code == requests.codes.ok:
                #print(req.text)
                return req.json()
            req.raise_for_status()
        except:
            raise
    
    def get_metadata_schema_fields(self, prefix):
        try:
            # print(f"get metadata fields for {prefix}")
            req = requests.get(self.__dspaceRestURL + "/api/core/metadatafields/search/bySchema", params={"schema": prefix}, headers={"Accept": "application/json"})
            if req.status_code == requests.codes.ok:
                return req.json()
            req.raise_for_status()
        except:
            raise