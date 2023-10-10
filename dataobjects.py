
from requests.cookies import RequestsCookieJar
import base64
import json

class ImporterData:
    """ shared data to be used by importer application """
    # a singleton
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    # may have to add self.lock = Threading.lock to __init__
    # method that wants to use a shared variable use with self.lock to acquire a lock for the variable then modify/read the variable
    def __init__(self) -> None:
        self.__cookie_jar = None
        self.__CSRF_token = ''
        self.__JWT = ''
        self.__JWT_decoded = {"header": "", "payload":"", "signature":""}

    # getters
    @property
    def cookie_jar(self):
        return self.__cookie_jar
    
    @property
    def csrf_token(self):
        return self.__CSRF_token
    
    @property
    def jwt(self):
        return self.__JWT

    @property
    def jwt_decoded(self):
        return self.__JWT_decoded
    
    @cookie_jar.setter
    def cookie_jar(self, value: RequestsCookieJar):
        self.__cookie_jar = value
    
    @csrf_token.setter
    def csrf_token(self, value):
        self.__CSRF_token = value
    
    @jwt.setter
    def jwt(self, value:str):
        self.__JWT = value
        token_comps = value.split(".")
        self.__JWT_decoded["header"] = json.loads(base64.urlsafe_b64decode(token_comps[0]).decode(encoding="utf-8"))
        self.__JWT_decoded["signature"] = token_comps[2]
        self.__JWT_decoded["payload"] = json.loads(base64.urlsafe_b64decode(token_comps[1]).decode(encoding="utf-8"))
        