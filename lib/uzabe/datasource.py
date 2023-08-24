from lib.uzabe.configs import ZDCConfig
from lib.uzabe.requests import ZDCRequest
from lib.uzabe.const import


class ZDCDataSource:
    def __init__(self):
        self._config = ZDCConfig()
        self._request = ZDCRequest()

    def get_list(self):
        _connect = self._config.load_register('token')
        if _connect:
            _response = self._request.execute_method('/datasource', 'GET', None, True)
            if self._request.response_status_code() ==
