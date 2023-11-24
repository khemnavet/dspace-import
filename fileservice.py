from pathlib import Path
from dataobjects import ItemFileMatchType

class ItemFileService:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def item_file_exists(self, file_name: str, file_name_matching: ItemFileMatchType, file_extension: str, item_directory: str) -> bool:
        return len(self.item_files(file_name, file_name_matching, file_extension, item_directory)) > 0
    
    def item_files(self, file_name: str, file_name_matching: ItemFileMatchType, file_extension: str, item_directory: str) -> list:
        item_dir = Path(item_directory)

        if file_name_matching == ItemFileMatchType.EXACT:
            file = item_dir/(file_name.strip()+file_extension)
            return [file] if file.exists() else []
        
        if file_name_matching == ItemFileMatchType.BEGINS:
            return list(item_dir.glob(file_name+"*"+file_extension))