import tomllib

from config import ImporterConfig
from metadataservice import MetadataService

if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = ImporterConfig(tomllib.load(f))

    #print(config)
    print(config.dspace_rest_url())
    metadata_service = MetadataService(config)
    metadata_service.populate_metadata_schemas()

    print(metadata_service.get_schema_fields("dc"))