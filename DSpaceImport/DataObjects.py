class Mapping(object):
    def __init__(self, colName, metadataField):
        self.id = id(self)
        self.metadataField = metadataField
        self.colName = colName
