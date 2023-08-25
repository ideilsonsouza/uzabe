import ujson as json
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.requests import ZDCRequest
from lib.uzabe.const import ZDCConsts

class ZDCDataSource:
    def __init__(self, device_id: str):
        self.config = ZDCConfig()
        self.request = ZDCRequest()
        self.const = ZDCConsts()
        self.device_id = device_id or self.config.load_register('id')

    def get_datasource_on(self):
        try:
            connect = self.config.load_register('token')
            if connect:
                if self.device_id:
                    data = {'id': self.device_id}
                    response = self.request.execute_method('/datasource', 'POST', data, True)

                    if self.request.response_status_code() == self.const.HTTPResponse.OK:

                        if response:
                            self.config.save_datasource(response)

                else:
                    print(f" Não informado o id do dispositivo ")
            else:
                print(f" Não informado o id do dispositivo ")

        except ValueError as e:
            print(f"Falha ao tentar obter as fontes de dados do dispositivo: \
                   {e}")

    @staticmethod
    def get_datasource():
        try:
            with open('/db/datasource.json', 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

