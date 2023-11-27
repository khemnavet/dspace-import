# dspace auth

import base64
import json
from requests import HTTPError

from config import ImporterConfig
from dspaceauthrequest import DspaceAuthRequest
from dataobjects import AuthData

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
        

    def __init__(self, config: ImporterConfig, authData: AuthData) -> None:
        self.__dspace_auth = DspaceAuthRequest(config.dspace_rest_url())
        self.__auth_data = authData

    # may have to use locks to set these variables
    def __save_cookie_csrf(self, response):
        self.__auth_data.auth_cookie = response.cookies
        self.__auth_data.csrf_token = response.headers["DSPACE-XSRF-TOKEN"]
    
    def __save_jwt(self, response):
        self.__auth_data.bearer_jwt = response.headers["Authorization"].split(" ")[1]
    
    def logon(self, username, password) -> bool:
        try:
            # get the CSRF token and cookie
            self.__save_cookie_csrf(self.__dspace_auth.auth_status())

            #print(self.__shared_data.cookie_jar)
            #print(self.__shared_data.csrf_token)
            # login
            response = self.__dspace_auth.password_logon(username, password, self.__auth_data.auth_cookie, self.__auth_data.csrf_token)
            self.__save_cookie_csrf(response)
            self.__save_jwt(response)

        except HTTPError as err:
            print(f"Exception during logon. Error code {err.response.status_code}, reason {err.response.reason}")
            raise AuthException(f"Error during logon. Error code {err.response.status_code}, reason {err.response.reason}")