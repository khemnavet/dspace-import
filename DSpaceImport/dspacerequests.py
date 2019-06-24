import requests
import urllib.parse
import json
import re

__all__ = ['DspaceRequests','LogonException']

class DspaceRequests(object):
    def __init__(self, config):
        self.config = config
        self.cookieJar = None

    """
     attempt logon to the dspace repository
     return requests.cookies.RequestsCookieJar
    """
    def dspace_logon(self, username, password):
        try:
            # test email is valid - regular expression
            _match = re.match('^([a-zA-Z\-\+_%]+(\.[a-zA-Z\-\+_%]+)*)@([a-zA-Z0-9\-]+)(\.[a-zA-Z0-9\-]+)*\.([a-zA-Z][a-zA-Z][a-zA-Z]*)$', username)
            if (_match is None):
                raise DSpaceException(self.config['Messages']['invalidUserName'])
            _req = requests.post(self.config['DSpace']['dspaceRestURL']+'/login', data={'email':urllib.parse.quote_plus(username, safe='@'),'password':password})
            if _req.status_code == requests.codes.unauthorized:
                # raise exception
                raise DSpaceException(self.config['Messages']['loginFailed'])
            if _req.status_code == requests.codes.ok:
                self.cookieJar = _req.cookies
                return _req.cookies
            # else other status codes
            _req.raise_for_status()
        except:
            raise

    def dspace_top_communities(self):
        try:
            print('get top communities')
            _req = requests.get(self.config['DSpace']['dspaceRestURL']+'/communities/top-communities?expand=subCommunities,collections', headers={'Accept':'application/json'}, cookies=self.cookieJar)
            if _req.status_code == requests.codes.ok:
                return json.loads(_req.content)
            _req.raise_for_status()
        except:
            raise

    def dspace_community(self, uuid):
        try:
            print('get community '+uuid)
            _match = re.match('^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}$', uuid)
            if (_match is None):
                raise DSpaceException(self.config['Messages']['invalidUUID'])
            _req = requests.get(self.config['DSpace']['dspaceRestURL']+'/communities/'+uuid+'?expand=subCommunities,collections', headers={'Accept':'application/json'}, cookies=self.cookieJar)
            if _req.status_code == requests.codes.ok:
                return json.loads(_req.content)
            _req.raise_for_status()
        except:
            raise

    def dspace_community_subCommunities(self, uuid):
        try:
            print('get subcommunities for {}'.format(uuid))
            _match = re.match('^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}$', uuid)
            if (_match is None):
                raise DSpaceException(self.config['Messages']['invalidUUID'])
            _req = requests.get(self.config['DSpace']['dspaceRestURL']+'/communities/'+uuid+'/communities', headers={'Accept':'application/json'}, cookies=self.cookieJar)
            if _req.status_code == requests.codes.ok:
                return json.loads(_req.content)
            _req.raise_for_status()
        except:
            raise

    def dspace_community_collections(self, uuid):
        try:
            print('get collections for community {}'.format(uuid))
            _match = re.match('^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}$', uuid)
            if (_match is None):
                raise DSpaceException(self.config['Messages']['invalidUUID'])
            _req = requests.get(self.config['DSpace']['dspaceRestURL']+'/communities/'+uuid+'/collections', headers={'Accept':'application/json'}, cookies=self.cookieJar)
            if _req.status_code == requests.codes.ok:
                return json.loads(_req.content)
            _req.raise_for_status()
        except:
            raise


class DSpaceException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
