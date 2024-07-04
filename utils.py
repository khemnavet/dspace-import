import re

from pandas import isnull

class Utils:

    @staticmethod
    def valid_uuid(uuid):
        _match = re.match('^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', uuid)
        if _match is None:
            return False
        return True
    
    @staticmethod
    def row_column_value(row: dict, column):
        if isnull(row[column]):
            return None
        str_value = (str(row[column])).strip()
        if len(str_value) == 0:
            return None
        return str_value