# dspace auth request

import requests
import urllib.parse

class DspaceAuthRequest:

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, dspaceRestURL) -> None:
        self.__dspaceRestURL = dspaceRestURL

    def auth_status(self):
        req = requests.get(self.__dspaceRestURL + "/api/authn/status", headers={"Accept":"application/json"})
        if req.status_code == requests.codes.ok:
            return req
        else:
            req.raise_for_status()
    
    def password_logon(self, username, password, cookie_jar, csrf_token):
        data = {'user':urllib.parse.quote_plus(username, safe='@'),'password':password}
        headers = {"X-XSRF-TOKEN": csrf_token, "Content-Type": "application/x-www-form-urlencoded"}
        req = requests.post(self.__dspaceRestURL + "/api/authn/login", data=data, headers=headers, cookies=cookie_jar)
        if req.status_code == requests.codes.ok:
            return req
        else:
            req.raise_for_status()
