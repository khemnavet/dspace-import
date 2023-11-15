from config import ImporterConfig
from dspaceauthservice import DspaceAuthService
from dspacerequest import DspaceItemRequest
from requests import HTTPError

class ItemException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
    

class ItemService:
    _self = None
    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig) -> None:
        auth_service = DspaceAuthService(config)
        self._item_request = DspaceItemRequest(config.dspace_rest_url(), auth_service.get_bearer_jwt(), auth_service.get_auth_cookies())

    def owning_collection(self, item_uuid: str):
        try:
            owning_coll_json = self._item_request.item_owning_collection(item_uuid)
            #owning_coll_uuid = owning_coll_json["uuid"]
            #print(f"item uuid {item_uuid}, owning collection {owning_coll_uuid}")
            return owning_coll_json["uuid"]
        except HTTPError as err:
            print(f"Exception getting owning collection for item {item_uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(err.response.reason)

#
