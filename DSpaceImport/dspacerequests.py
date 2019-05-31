import requests
import urllib.parse

__all__ = ['DspaceRequests','LogonException']

class DspaceRequests(object):
    def __init__(self, config):
        self.config = config

    """
     attempt logon to the dspace repository
     return requests.cookies.RequestsCookieJar
    """
    def dspace_logon(self, username, password):
        try:
            req = requests.post(self.config['DSpace']['dspaceRestURL']+self.config['DSpace']['loginEndPoint'], data={'email':urllib.parse.quote_plus(username),'password':password})
            if req.status_code == requests.codes.unauthorized:
                # raise exception
                raise LogonException(self.config['Messages']['loginFailed'])
            if req.status_code == requests.codes.ok:
                return req.cookies
            # else other status codes
            req.raise_for_status()
        except:
            raise

class LogonException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

