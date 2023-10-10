# dspace auth request

import requests
import urllib.parse

from dataobjects import ImporterData

class DspaceAuthRequest:

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, dspaceRestURL, importerData: ImporterData) -> None:
        self.__dspaceRestURL = dspaceRestURL
        self.__importer_data = importerData

    def __save_cookie_csrf(self, response):
        self.__importer_data.cookie_jar = response.cookies
        self.__importer_data.csrf_token = response.headers["DSPACE-XSRF-TOKEN"]

    def auth_status(self):
        req = requests.get(self.__dspaceRestURL + "/api/authn/status", headers={"Accept":"application/json"})
        if req.status_code == requests.codes.ok:
            response = req.json()
            # get cookie jar and csrf token
            self.__save_cookie_csrf(req)
        else:
            req.raise_for_status()
    
    def password_logon(self, username, password, cookie_jar, csrf_token):
        data = {'user':urllib.parse.quote_plus(username, safe='@'),'password':password}
        headers = {"X-XSRF-TOKEN": csrf_token, "Content-Type": "application/x-www-form-urlencoded"}
        req = requests.post(self.__dspaceRestURL + "/api/authn/login", data=data, headers=headers, cookies=cookie_jar)
        if req.status_code == requests.codes.ok:
            # login successful 
            # get the csrf tokens
            self.__save_cookie_csrf(req)
            # get the JWT (Remove "Bearer ")
            self.__importer_data.jwt = req.headers["Authorization"].split(" ")[1]
        else:
            req.raise_for_status()
