from pathlib import Path
from pandas import ExcelFile, DataFrame, isna

class ExcelFileException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ExcelFileService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            print("create new instance of excel file service")
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self) -> None:
        #self.__dataframe = DataFrame()
        self.__sheet = ""
    
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
    
    def set_column_headings(self, sheet_name) -> None:
        try:
            self.__selected_sheet = sheet_name
            #print(sheet_name)
            self.__dataframe = self.__excel_file_obj.parse(sheet_name=sheet_name, header=0)
            # self.__import_columns = list(self.__dataframe.columns.values)
            #print(list(self.__dataframe.columns.values))
            #print(self.__dataframe.info())
        except Exception as e:
            print(f"Error getting columns from excel file object: {str(e)}")
            raise ExcelFileException(str(e))
    
    def get_column_headings(self):
        import_columns = list(self.__dataframe.columns.values)
        print(f"in get column headings: {import_columns} from sheet {self.__selected_sheet}")
        return import_columns
    
    def reset_file(self):
        self.__dataframe.reset_index()

    def file_itemuuiud_title(self, file_column, item_uuid_column, title_column):
        for row in self.__dataframe.iterrows(): # row is a tuple, 0 = index, 1 = data
            data = row[1]
            file = None
            itemuuid = None
            if not isna(data[file_column]) and len((data[file_column]).strip()) > 0:
                file = data[file_column]
            if not isna(data[item_uuid_column]) and len((data[item_uuid_column]).strip()) > 0:
                itemuuid = data[item_uuid_column]
            
            yield (file, itemuuid, data[title_column])
    
    def num_rows(self):
        return len(self.__dataframe.index)