from config import ImporterConfig
from dspaceauthservice import DspaceAuthService
from dspacerequest import DspaceItemRequest
from dataobjects import BundleType, Item, Bundle, DSO, AuthData
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
    
    def __init__(self, config: ImporterConfig, auth_data: AuthData) -> None:
        self._item_request = DspaceItemRequest(config.dspace_rest_url(), auth_data)

    def owning_collection(self, item_uuid: str):
        try:
            owning_coll_json = self._item_request.item_owning_collection(item_uuid)
            #owning_coll_uuid = owning_coll_json["uuid"]
            #print(f"item uuid {item_uuid}, owning collection {owning_coll_uuid}")
            return owning_coll_json["uuid"]
        except HTTPError as err:
            print(f"Exception getting owning collection for item {item_uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(f"Error getting owning collection for item {item_uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
        except Exception as err1:
            print(f"Exception getting owning collection for item {item_uuid}. Error: {str(err1)}")
            raise ItemException(f"Error getting owning collection for item {item_uuid}. Error: {str(err1)}")
    
    def _populate_item(self, item_json) -> Item:
        return Item(item_id=item_json["id"], uuid=item_json["uuid"], name=item_json["name"], handle=item_json["handle"], existing_metadata=item_json["metadata"], in_archive=item_json["inArchive"], discoverable=item_json["discoverable"], withdrawn=item_json["withdrawn"])

    def get_item(self, item_uuid) -> Item:
        try:
            return self._populate_item(self._item_request.get_item(item_uuid))
        except HTTPError as err:
            print(f"Exception getting item for uuid {item_uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(f"Error getting item for uuid {item_uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
        except Exception as err1:
            print(f"Exception getting item for uuid {item_uuid}. Error: {str(err1)}")
            raise ItemException(f"Error getting item for uuid {item_uuid}. Error: {str(err1)}")


    def _find_bundle(self, item_bundles, bundle_type: BundleType):
        result = None
        for bundle in item_bundles["_embedded"]["bundles"]:
            if bundle["name"] == bundle_type.name:
                result = Bundle(uuid=bundle["uuid"], bundle_type=bundle_type)
                break
        return result

    def bundle(self, item: Item, bundle_types: list):
        try:
            result = []
            item_bundles = self._item_request.item_bundles(item.uuid)
            # none if bundle does not exist
            for bundle_type in bundle_types:
                result.append(self._find_bundle(item_bundles, bundle_type))
            return tuple(result)

        except HTTPError as err:
            print(f"Exception getting bundles for item {item.uuid} {item.name}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(f"Error getting bundles for item {item. uuid} {item.name}. Error code {err.response.status_code}, reason {err.response.reason}")
        except Exception as err1:
            print(f"Exception getting bundles for item {item.uuid} {item.name}. Error: {str(err1)}")
            raise ItemException(f"Error getting bundles for item {item.uuid} {item.name}. Error: {str(err1)}")
    
    def create_item(self, item: Item, owning_collection: DSO) -> Item:
        try:
            return self._populate_item(self._item_request.new_item(item.to_json_str(), owning_collection.uuid))
        
        except HTTPError as err:
            print(f"Exception creating item {item.name}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(f"Error creating item {item.name}. Error code {err.response.status_code}, reason {err.response.reason}")
        except Exception as err1:
            print(f"Exception creating item {item.name}. Error: {str(err1)}")
            raise ItemException(f"Error creating item {item.name}. Error: {str(err1)}")

    def update_item(self, item: Item) -> Item:
        try:
            return self._populate_item(self._item_request.patch_item(item.uuid, item.to_patch_str()))
        
        except HTTPError as err:
            print(f"Exception updating item {item.uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise ItemException(f"Error updating item {item.uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
        except Exception as err1:
            print(f"Exception updating item {item.uuid}. Error: {str(err1)}")
            raise ItemException(f"Error updating item {item.uuid}. Error: {str(err1)}")

#
