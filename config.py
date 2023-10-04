
class ImporterConfig:
    def __init__(self, config) -> None:
        self.__config = config

    def dspace_rest_url(self) -> str:
        return self.__config["DSpace"]["dspaceRestURL"]