import ntptime
import machine
import time
import ujson as json
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.requests import ZDCRequest
from lib.uzabe.const import ZDCConsts
from lib.uzabe.network import ZDCNetwork

class ZDCDevice:
    def __init__(self):
        self.const = ZDCConsts()
        self.config = ZDCConfig()
        self.network = ZDCNetwork()
        self.mac = self.network.get_network_mac()
        self.ip = self.network.get_network_ip()
        self.name = self.config.load_register('name')
        self.id = self.config.load_register('id') or self.mac

    @property
    def apply_for_registration(self):
        """VERIFICAÇÃO DO DISPOSITIVO NO SERVIDOR"""
        try:
            auto_register = ZDCRequest()
            get_device = ZDCRequest()
            data = {'mac': self.mac, 'nome': self.name, 'ip': self.ip}
            auto_register.execute_method('/devices/auto-register', "POST", data, False)

            #VERIFICAR SE O DISPOSITIVO FOI REGISTRADO COM EXITO
            #DEVE SER RETORNADO FALSE PARA QUE O LOOP CONTINUE
            if auto_register.response_status_code() == self.const.HTTPResponse.CREATED:
                print(f"Device registered to server with mac: {self.mac}")
                return False

            #VERIFICA SE O DISPOSITIVO ESTA CADASTRADO E SOLICITA OS DADOS PARA ACESSO
            elif auto_register.response_status_code() == self.const.HTTPResponse.OK:
                response = get_device.execute_method(f"/devices/check/{self.mac}", "GET", None, False)
                if get_device.response_status_code() == self.const.HTTPResponse.OK:
                    email = response.get('email')
                    password = response.get('password')
                    device_id = response.get('id')

                    #VERIFICA SE OS DADOS FOI RECEBIDO CORRETAMENTE E OS SALVA LOCALMENTE
                    #SE TODOS OS VALORES FOI RECBIDO E SALVOS LOCALMENTE O RETORNO DEVE SER TRUE
                    if email and password and device_id:
                        self.config.save_register('api_user', email, False)
                        self.config.save_register('api_pass', password, False)
                        self.config.save_register('id', device_id)
                        return True

            #VERIFICA SE O DISPOSITIVO JÁ FOI CONFIGURADO NO SERVIDOR
            #O RETORNO DEVE SER FALSE PARA O LOOP CONTINUE ATE QUE SEJA LIBERADO NO SERVIDOR
            elif auto_register.response_status_code() == self.const.HTTPResponse.UNAUTHORIZED:
                print(f"Device is registered but not configured yet \
                        mac: {self.mac}, is ready to be configured ")
                return False

            #VERIFICA SE O DISPOSITIVO NÃO FOI REGISTRADO NO SERVIDOR
            #NESTE EVENTO E CRIADO UM ALERTA INFORMANDO QUE O DISPOSITIVO NÃO PODE SER REGISTRADO
            elif auto_register.response_status_code() == self.const.HTTPResponse.UNPROCESSABLE_ENTITY:
                device_event = ZDCRequest()
                description = f"Device mac:{self.mac} was not correctly registered with the server."
                data = {'event': 'Device ZDAC', 'description':description, 'origin':self.mac }
                device_event.execute_method('/events', "POST", data, False)

                #VERIFICADO SE O DISPOSITIVO JÁ TEM OS DADOS NECESSARIOS PARA FAZER O ENVIO
                email = self.config.load_register('api_user', None, False)
                password = self.config.load_register('api_pass', None, False)
                device_id = self.config.load_register('api_pass', None, False)
                token = self.config.load_register('token', None, False)

                # VERIFICADO SE O DISPOSITIVO JÁ TEM OS DADOS NECESSARIOS PARA FAZER O ENVIO
                if email and password and device_id and token:
                    return True
                else:
                    return False

            #VERIFICA SE O RETORNO FOI DIFERENTE DE CRIAÇÃO E SOLICITAÇÃO DOS DADOS
            #MAS SE O DISPOSITIVO JÁ TIVER OS DADOS NECESSARIOS O LOOP E ENCERRADO
            elif not auto_register.response_status_code() in  [self.const.HTTPResponse.CREATED,
                                                             self.const.HTTPResponse.OK,
                                                             self.const.HTTPResponse.UNAUTHORIZED]:
                email = self.config.load_register('api_user',None, False)
                password = self.config.load_register('api_pass',None, False)
                device_id = self.config.load_register('api_pass',None, False)
                token = self.config.load_register('token',None, False)

                # MAS SE O DISPOSITIVO JÁ TIVER OS DADOS NECESSARIOS O LOOP E ENCERRADO
                if email and password and device_id and token:
                    return True
                else:
                    return False
            else:
                return False
        except (OSError, ValueError):
            # MAS SE O DISPOSITIVO JÁ TIVER OS DADOS NECESSARIOS O LOOP E ENCERRADO
            email = self.config.load_register('api_user', None, False)
            password = self.config.load_register('api_pass', None, False)
            device_id = self.config.load_register('api_pass', None, False)
            token = self.config.load_register('token', None, False)

            # MAS SE O DISPOSITIVO JÁ TIVER OS DADOS NECESSARIOS O LOOP E ENCERRADO
            if email and password and device_id and token:
                return True
            else:
                return False

    def sync_data(self):
        ntptime.settime()
        (year, month, day, weekday, hour, minute, second, millisecond) = rtc.datetime()
        hour = (hour - 3) % 24
        self.rtc.datetime((year, month, day, weekday, hour, minute, second, millisecond))

    def current_date(self):
        self.sync_data()
        current_datetime = self.rtc.datetime()
        "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(current_datetime[0], current_datetime[1],
                                                           current_datetime[2], current_datetime[4],
                                                           current_datetime[5], current_datetime[6])
        return current_datetime

    def get_command(self):
        command_request = ZDCRequest()
        response = command_request.execute_method(f"/devices/command/{self.id}", "GET", None, False)
        if command_request.response_status_code() == 200:
            return response.get('command')
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
