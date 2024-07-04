from pathlib import Path
from pandas import ExcelFile
from utils import Utils

class ExcelFileException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ExcelFileService:
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            #print("create new instance of excel file service")
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
            raise ExcelFileException(f"Error creating excel file object: {str(e)}")
    
    def get_sheet_names(self) -> list:
        return self.__excel_file_obj.sheet_names
    
    def set_column_headings(self, sheet_name) -> None:
        try:
            self.__selected_sheet = sheet_name
            #print(sheet_name)
            self.__dataframe = self.__excel_file_obj.parse(sheet_name=sheet_name, header=0)
            # convert all data in the dataframe to string
            # self.__dataframe = self.__dataframe.map(str)
        except Exception as e:
            print(f"Error getting columns from excel file object: {str(e)}")
            raise ExcelFileException(f"Error getting columns from excel file object: {str(e)}")
    
    def get_column_headings(self):
        import_columns = list(self.__dataframe.columns.values)
        #print(f"in get column headings: {import_columns} from sheet {self.__selected_sheet}")
        return import_columns
    
    def reset_file(self):
        self.__dataframe.reset_index()

    def file_itemuuiud_title(self, file_column, item_uuid_column, title_column):
        for row in self.__dataframe.iterrows(): # row is a tuple, 0 = index, 1 = data
            index = row[0]
            data = row[1]
            file = Utils.row_column_value(data, file_column)
            itemuuid = Utils.row_column_value(data, item_uuid_column) if len(item_uuid_column) > 0 else None
            
            yield (index, file, itemuuid, data[title_column])
    
    def num_rows(self):
        return len(self.__dataframe.index)
    
    def get_row(self, row_num):
        if row_num > len(self.__dataframe.index):
            return {}
        return self.__dataframe.iloc[row_num]
    
    def primary_bitstream_value(self, row_num, primary_bitstream_column):
        row = self.__dataframe.iloc[row_num]
        return Utils.row_column_value(row, primary_bitstream_column)
    
    def item_metadata(self, row_num, metadata_mapping: dict):
        result = {}
        row = self.__dataframe.iloc[row_num]
        for metadata_field, columns in metadata_mapping.items():
            row_metadata = []
            place = 0
            for col in columns:
                col_value = Utils.row_column_value(row, col)
                if col_value is not None:
                    row_metadata.append({"value": col_value, "language": None, "authority": None, "confidence": -1, "place": place})
                    place = place + 1
            if len(row_metadata) > 0:
                result[metadata_field] = list(row_metadata) 
        return result