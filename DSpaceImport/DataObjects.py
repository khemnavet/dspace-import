from enum import Enum

class Mapping(object):
    def __init__(self, colName, metadataField):
        self.id = id(self)
        self.metadataField = metadataField
        self.colName = colName

class DSOTypes(Enum):
    COMMUNITY = 1
    COLLECTION = 2

class DSO(object):
    def __init__(self, uuid, name, parent, type, itemsLoaded=False):
        self.id = id(self)
        self.uuid = uuid
        self.name = name
        self.parent = parent
        self.type = type
        self.itemsLoaded = itemsLoaded
        self.children = []
        self.collections = []

    def addChild(self, childId):
        self.children.append(childId)

    def addCollection(self, collId):
        self.collections.append(collId)

    def isCommunity(self):
        return self.type == DSOTypes.COMMUNITY

    def isCollection(self):
        return self.type == DSOTypes.COLLECTION

