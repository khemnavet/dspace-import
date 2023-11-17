# dspace auth

import base64
import json
from requests import HTTPError

from config import ImporterConfig
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
        

    def __init__(self, config: ImporterConfig) -> None:
        self.__dspace_auth = DspaceAuthRequest(config.dspace_rest_url())
        self.__jwt = ''
        self.__cookie_jar = None
        self.__CSRF_token = ''
        self.__jwt_decoded = {"header": "", "payload":"", "signature":""}

    # may have to use locks to set these variables
    def __save_cookie_csrf(self, response):
        self.__cookie_jar = response.cookies
        self.__CSRF_token = response.headers["DSPACE-XSRF-TOKEN"]
    
    def __save_jwt(self, response):
        self.__jwt = response.headers["Authorization"].split(" ")[1]
        token_comps = self.__jwt.split(".")
        self.__jwt_decoded["header"] = json.loads(base64.urlsafe_b64decode(token_comps[0]).decode(encoding="utf-8"))
        self.__jwt_decoded["signature"] = token_comps[2]
        self.__jwt_decoded["payload"] = json.loads(base64.urlsafe_b64decode(token_comps[1]).decode(encoding="utf-8"))
    
    def logon(self, username, password) -> bool:
        try:
            # get the CSRF token and cookie
            self.__save_cookie_csrf(self.__dspace_auth.auth_status())

            #print(self.__shared_data.cookie_jar)
            #print(self.__shared_data.csrf_token)
            # login
            response = self.__dspace_auth.password_logon(username, password, self.__cookie_jar, self.__CSRF_token)
            self.__save_cookie_csrf(response)
            self.__save_jwt(response)

        except HTTPError as err:
            print(f"Exception during logon. Error code {err.response.status_code}, reason {err.response.reason}")
            raise AuthException(f"Error during logon. Error code {err.response.status_code}, reason {err.response.reason}")

    # may have to use locks to access these variables - cookie_jar and jwt
    def get_auth_cookies(self):
        return self.__cookie_jar
    
    def get_bearer_jwt(self):
        return "Bearer " + self.__jwt
    
    def get_csrf_token(self):
        return self.__CSRF_token