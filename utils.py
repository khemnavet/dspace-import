import re

class Utils:

    @staticmethod
    def valid_uuid(uuid):
        _match = re.match('^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}$', uuid)
        if _match is None:
            return False
        return True