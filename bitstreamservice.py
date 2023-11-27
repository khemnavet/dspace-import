from config import ImporterConfig
from dspacerequest import DspaceBitstreamRequest
from dataobjects import Bitstream, Bundle, AuthData
from requests import HTTPError
from pathlib import Path

class BitstreamException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class BitstreamService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self, config: ImporterConfig, auth_data: AuthData) -> None:
        self._bitstream_request = DspaceBitstreamRequest(config.dspace_rest_url(), auth_data)
    
    def remove_bitstream(self, bitstream: Bitstream):
        try:
            _ = self._bitstream_request.delete_bitstream(bitstream.uuid)
        except HTTPError as err:
            print(f"Exception removing bitstream {bitstream.uuid} ({bitstream.name}). Error code {err.response.status_code}, reason {err.response.reason}")
            raise BitstreamException(f"Error removing bitstream {bitstream.uuid} ({bitstream.name}). Error code {err.response.status_code}, reason {err.response.reason}")
    
    def _populate_bitstream(self, bitstream_json) -> Bitstream:
        return Bitstream(bitstream_json["id"], bitstream_json["uuid"], bitstream_json["name"])
    
    def create_bitstream(self, bundle: Bundle, file: Path) -> Bitstream:
        try:
            return self._populate_bitstream(self._bitstream_request.new_bitstream(bundle.uuid, file))
        except HTTPError as err:
            print(f"Exception creating bitstream for bundle {bundle.name} ({bundle.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")
            raise BitstreamException(f"Error creating bitstream for bundle {bundle.name} ({bundle.uuid}). Error code {err.response.status_code}, reason {err.response.reason}")
    