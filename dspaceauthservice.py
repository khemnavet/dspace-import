# dspace auth

from requests import HTTPError

from config import ImporterConfig
from dataobjects import ImporterData
from dspaceauthrequest import DspaceAuthRequest

class AuthException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class DspaceAuthService:

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
        

    def __init__(self, config: ImporterConfig, shared_data: ImporterData) -> None:
        self.__shared_data = shared_data
        self.__dspace_auth = DspaceAuthRequest(config.dspace_rest_url(), shared_data)
    
    def logon(self, username, password) -> bool:
        try:
            # get the CSRF token and cookie
            self.__dspace_auth.auth_status()
            #print(self.__shared_data.cookie_jar)
            #print(self.__shared_data.csrf_token)
            # login
            self.__dspace_auth.password_logon(username, password, self.__shared_data.cookie_jar, self.__shared_data.csrf_token)

        except HTTPError as err:
            print(f"Exception during logon. Error code {err.response.status_code}, reason {err.response.reason}")
            raise AuthException(err.response.reason)
