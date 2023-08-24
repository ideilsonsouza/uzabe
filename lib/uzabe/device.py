import ntptime
import machine
import time
import ujson as json
from uzrequests import ZDCRequest
from uznetwork import ZDCNetwork
from uzconfigs import ZDCCredentials

sys_network = ZDCNetwork()
sys_credentials = ZDCCredentials()


class ZDCDevice:
    def __init__(self):
        self.mac = sys_network.get_network_mac()
        self.ip = sys_network.get_network_ip()
        self.name = sys_credentials.load_register('device_name')


    def register_on_server(self):
        sys_request = ZDCRequest()
        data = {'mac':self.mac, 'nome':self.name, 'ip':self.ip }
        HTTPResponse  =  sys_request.execute_post('/devices/check', data, include_token=False)
        if  sys_request.response_status_code() == 200:
            print(HTTPResponse.get('message'))
            return True
        else:
            if sys_request.response_status_code() == 422:
                descricao = f"Dispositivo mac:{self.mac} não foi registrado corretamento no sistema."
                data = {'evento': 'Dispositivo ZDAC', 'descricao':descricao, 'origem':self.mac }
                sys_request.execute_post('/events', data, include_token=False)

            if sys_request.response_status_code() == 503:
                print("Servidor em manutenção")

            if sys_request.response_status_code() == 500:
                print("Servidor não esta acessivel no momento")

            if sys_request.response_status_code() == 404:
                print("Endereço não esta mais acessivel")
                descricao = f"Dispositivo mac:{self.mac} recebeu o erro 404 ao tentar se registrar"
                data = {'evento': 'Dispositivo ZDAC', 'descricao':descricao, 'origem':self.mac }
                sys_request.execute_post('/devices', data, include_token=False)

            print(HTTPResponse.get('message'))
            return False

    def get_device_infor(self):
        sys_request = ZDCRequest()
        device_id = sys_credentials.load_register('id')

    def set_sincro_timer(self):
        ntptime.settime()
        (year, month, day, weekday, hour, minute, second, millisecond) = rtc.datetime()
        hour = (hour - 3) % 24
        self.rtc.datetime((year, month, day, weekday, hour, minute, second, millisecond))

    def current_datetime(self):
        self.set_sincro_timer()
        current_datetime = self.rtc.datetime()
        "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(current_datetime[0], current_datetime[1],
                                                           current_datetime[2], current_datetime[4],
                                                           current_datetime[5], current_datetime[6])
        return current_datetime

    def get_command(self):
        sys_request = ZDCRequest()
        HTTPResponse = sys_request.execute_get('/devices/command/' + self.mac)
        if sys_request.response_status_code() == 200:
            print(HTTPResponse.get('command'))
            HTTPResponse = sys_request.execute_delete('/devices/command/' + self.mac)
            print(f" 'Função para executar os comandos '{HTTPResponse.get('command')}")
        else:
            return True

    def get_data_sources(self):
        sys_request = ZDCRequest()
        HTTPResponse = sys_request.execute_get('/devices/getdatasources')

        if sys_request.response_status_code() == 200:
            return HTTPResponse.get('data')
        else:
            print(HTTPResponse.get('message'))
            return None

    def get_user(self):
        sys_request = ZDCRequest()
        HTTPResponse = sys_request.execute_get('/devices/check/' + self.mac , include_token=False)
        if sys_request.response_status_code() == 200:
            print(HTTPResponse.get('message'))
            sys_credentials.save_register('api_email', HTTPResponse.get('email'))
            sys_credentials.save_register('api_password', HTTPResponse.get('password'))
            sys_credentials.save_register('id', HTTPResponse.get('id'))
            return True
        else:
            print(HTTPResponse.get('message'))
            return False

    @staticmethod
    def login():
        email = sys_credentials.load_register('api_email')
        password = sys_credentials.load_register('api_password')
        sys_request = ZDCRequest()
        data = {'email': email, 'password': password, 'module':"ZDAC-ESP" }
        HTTPResponse = sys_request.execute_post("/users/login", data, include_token=False)
        if sys_request.response_status_code() == 200:
            print("Usuário logado no sistema")
            sys_credentials.save_register('token', HTTPResponse.get('token'))
            return True
        else:
            print(HTTPResponse.get('message'))
            return False
