__all__ = ['MetadataSchema']

class Metadata:
    def exact_name(self) -> str:
        """The exact fully qualified field, should use the syntax schema.element.qualifier or schema.element if no qualifier exists (e.g. "dc.title", "dc.contributor.author")."""
        pass

class MetadataField(Metadata):
    def __init__(self, fieldId: int, element: str, qualifier: str) -> None:
        self.__fieldId = fieldId
        self.__element = element
        self.__qualifier = qualifier
    
    @property
    def fieldId(self) -> int:
        return self.__fieldId
    
    @property
    def element(self) -> str:
        return self.__element

    @property
    def qualifier(self) -> str:
        return self.__qualifier
    
    def exact_name(self) -> str:
        return self.element if self.qualifier is None else self.element + "." + self.qualifier
    
class MetadataSchema(Metadata):
    def __init__(self, prefix: str) -> None:
        self.__prefix = prefix
        self.__fields = []

    def prefix(self) -> str:
        return self.__prefix

    def fields(self) -> list:
        return self.__fields

    def add(self, metadata: Metadata) -> None:
        self.fields().append(metadata)
    
    def exact_name(self) -> str:
        for field in self.fields():
            yield self.prefix() + "." + field.exact_name()