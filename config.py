
class ImporterConfig:
    def __init__(self, config) -> None:
        self.__config = config

    def dspace_rest_url(self) -> str:
        return self.__config["DSpace"]["dspaceRestURL"]
    
    def locale(self) -> str:
        return self.__config["locale"]
    
    def window_width(self) -> int:
        return int(self.__config["wizardWidth"])
    
    def window_height(self) -> int:
        return int(self.__config["wizardHeight"])