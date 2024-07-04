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
        files = []

        if file_name_matching == ItemFileMatchType.EXACT:
            # file_name may be multiple files with optional description for each
            # file1.ext|file1 description;file2.ext|file2 description
            for file_desc in file_name.strip().split(";"):
                fd = (file_desc+"|").split("|")
                file = item_dir/(fd[0].strip()+file_extension)
                if file.exists():
                    files.append({"file": file, "description": fd[1].strip()})
        
        if file_name_matching == ItemFileMatchType.BEGINS:
            for file in list(item_dir.glob(file_name+"*"+file_extension)):
                files.append({"file":file, "description": ""})

        return files