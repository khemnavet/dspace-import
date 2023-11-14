import re

class Utils:

    @staticmethod
    def valid_uuid(uuid):
        match = re.match('^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}$', uuid)
        return match is None