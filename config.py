class ConfigException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ImporterConfig:
    WIZARD_WIDTH = "wizardWidth"
    WIZARD_HEIGHT = "wizardHeight"

    def __init__(self, config) -> None:
        self.__config = config
        self._validate_positive_integer(self.WIZARD_WIDTH)
        self._validate_positive_integer(self.WIZARD_HEIGHT)

    def _validate_positive_integer(self, setting):
        if not self._is_integer(self.__config[setting]):
            raise ConfigException(f"The {setting} configuration value has to be an integer")
        if int(self.__config[setting]) <= 0:
            raise ConfigException(f"The {setting} configuration value has to be a positive number")
        return True

    def _is_integer(self, str):
        try:
            val = float(str)
        except ValueError:
            return False
        else:
            return val.is_integer()

    def dspace_rest_url(self) -> str:
        return self.__config["DSpace"]["dspaceRestURL"]
    
    def locale(self) -> str:
        return self.__config["locale"]
    
    def window_width(self) -> int:
        return int(self.__config[self.WIZARD_WIDTH])
    
    def window_height(self) -> int:
        return int(self.__config[self.WIZARD_HEIGHT])