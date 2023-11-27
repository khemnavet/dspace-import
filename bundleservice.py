from config import ImporterConfig
from dspacerequest import DspaceBundleRequest
from dataobjects import Bundle, Bitstream, Item, AuthData
from requests import HTTPError

class BundleException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class BundleService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, auth_data: AuthData) -> None:
        self._bundle_request = DspaceBundleRequest(config.dspace_rest_url(), auth_data)
    
    def bundle_has_primary_bitstream(self, bundle: Bundle):
        return self._bundle_request.has_primary_bitstream(bundle.uuid)
    
    def remove_primary_bitstream(self, bundle: Bundle):
        try:
            resp = self._bundle_request.delete_primary_bitstream_flag(bundle.uuid)
        except HTTPError as err:
            print(f"Exception removing primary bitstream flag for bundle {bundle.uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise BundleException(f"Error removing primary bitstream flag for bundle {bundle.name}. Error code {err.response.status_code}, reason {err.response.reason}")
    
    def _populate_bitstream(self, bitstream):
        return Bitstream(bitstream_id=bitstream["id"], uuid=bitstream["uuid"], name=bitstream["name"])

    def bundle_bitstreams(self, bundle: Bundle):
        try:
            result = []
            curr_page = 0
            total_pages = 1
            while curr_page < total_pages:
                bitstream_json = self._bundle_request.get_bitstreams(bundle.uuid, curr_page)
                total_pages = bitstream_json["page"]["totalPages"]
                for bitstream in bitstream_json["_embedded"]["bitstreams"]:
                    result.append(self._populate_bitstream(bitstream))
                curr_page = curr_page + 1
            
            return result
        except HTTPError as err:
            print(f"Exception getting bitstreams for bundle {bundle.uuid}. Error code {err.response.status_code}, reason {err.response.reason}")
            raise BundleException(f"Exception getting bitstreams for bundle {bundle.name}. Error code {err.response.status_code}, reason {err.response.reason}")
    
    def create_bundle(self, bundle: Bundle, item: Item) -> Bundle:
        try:
            new_bundle = self._bundle_request.new_bundle(bundle.to_json_str(), item.uuid)
            bundle.uuid = new_bundle["uuid"]
            return bundle
        
        except HTTPError as err:
            print(f"Exception creating bundle {bundle.name} for item {item.name} ({item.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")
            raise BundleException(f"Error creating bundle {bundle.name} for item {item.name} ({item.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")
    
    def bundle_add_primary_bitstream(self, bundle: Bundle, bitstream: Bitstream):
        try:
            _ = self._bundle_request.add_primary_bitstream(bundle.uuid, bitstream.uuid)
        except HTTPError as err:
            print(f"Exception setting primary bitstream for bundle {bundle.name} ({bundle.uuid}) to {bitstream.name} ({bitstream.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")
            raise BundleException(f"Error setting primary bitstream for bundle {bundle.name} ({bundle.uuid}) to {bitstream.name} ({bitstream.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")