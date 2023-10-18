from pathlib import Path
from pandas import ExcelFile

class ExcelFileException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ExcelFileService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self) -> None:
        pass
    
    def set_file(self, file_name) -> None:
        try:
            self.__file_name = file_name
            import_file = Path(file_name)
            self.__excel_file_obj = ExcelFile(import_file)
        except Exception as e:
            print(f"Error creating excel file object: {str(e)}")
            raise ExcelFileException(str(e))
    
    def get_sheet_names(self) -> list:
        return self.__excel_file_obj.sheet_names