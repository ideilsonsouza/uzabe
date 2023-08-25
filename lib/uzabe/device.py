import ntptime
import time
from machine import RTC
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.requests import ZDCRequest
from lib.uzabe.const import ZDCConsts
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.command import ZDCCommand


class ZDCDevice:
    def __init__(self):
        self.const = ZDCConsts()
        self.config = ZDCConfig()
        self.network = ZDCNetwork()
        self.command = ZDCCommand()
        self.mac = self.network.get_lan_mac() or self.network.get_wlan_mac()
        self.ip = self.network.get_lan_ip() or self.network.get_wlan_ip()
        self.name = self.config.load_register('name')
        self.id = self.config.load_register('id') or self.mac
        self.rtc = RTC()

    @property
    def apply_for_registration(self) -> bool:
        """VERIFICAÇÃO DO DISPOSITIVO NO SERVIDOR"""
        try:
            auto_register = ZDCRequest()
            get_device = ZDCRequest()
            data = {'mac': self.mac, 'nome': self.name, 'ip': self.ip}
            auto_register.execute_method('/devices/auto-register', "POST", data, False)

            # VERIFICAR SE O DISPOSITIVO FOI REGISTRADO COM EXITO
            # DEVE SER RETORNADO FALSE PARA QUE O LOOP CONTINUE
            if auto_register.response_status_code() == self.const.HTTPResponse.CREATED:
                print(f"Device registered to server with mac: {self.mac}")
                return False

            # VERIFICA SE O DISPOSITIVO ESTA CADASTRADO E SOLICITA OS DADOS PARA ACESSO
            elif auto_register.response_status_code() == self.const.HTTPResponse.OK:
                response = get_device.execute_method(f"/devices/check/{self.mac}", "GET", None, False)
                if get_device.response_status_code() == self.const.HTTPResponse.OK:
                    email = response.get('email')
                    password = response.get('password')
                    device_id = response.get('id')

                    # VERIFICA SE OS DADOS FOI RECEBIDO CORRETAMENTE E OS SALVA LOCALMENTE
                    # SE TODOS OS VALORES FOI RECBIDO E SALVOS LOCALMENTE O RETORNO DEVE SER TRUE
                    if email and password and device_id:
                        self.config.save_register('api_user', email, False)
                        self.config.save_register('api_pass', password, False)
                        print(device_id)
                        self.config.save_register('id', device_id, encode=False)
                        return True

            # VERIFICA SE O DISPOSITIVO JÁ FOI CONFIGURADO NO SERVIDOR
            # O RETORNO DEVE SER FALSE PARA O LOOP CONTINUE ATE QUE SEJA LIBERADO NO SERVIDOR
            elif auto_register.response_status_code() == self.const.HTTPResponse.UNAUTHORIZED:
                print(f"Device is registered but not configured yet \
                        mac: {self.mac}, is ready to be configured ")
                return False

            # VERIFICA SE O DISPOSITIVO NÃO FOI REGISTRADO NO SERVIDOR
            # NESTE EVENTO E CRIADO UM ALERTA INFORMANDO QUE O DISPOSITIVO NÃO PODE SER REGISTRADO
            elif auto_register.response_status_code() == self.const.HTTPResponse.UNPROCESSABLE_ENTITY:
                device_event = ZDCRequest()
                description = f"Device mac:{self.mac} was not correctly registered with the server."
                data = {'event': 'Device ZDAC', 'description': description, 'origin': self.mac}
                device_event.execute_method('/events', "POST", data, False)

                # VERIFICADO SE O DISPOSITIVO JÁ TEM OS DADOS NECESSARIOS PARA FAZER O ENVIO
                email = self.config.load_register('api_user', None, False)
                password = self.config.load_register('api_pass', None, False)
                device_id = self.config.load_register('api_pass', None, False)
                token = self.config.load_register('token', None, False)

                # VERIFICADO SE O DISPOSITIVO JÁ TEM OS DADOS NECESSARIOS PARA FAZER O ENVIO
                if email and password and device_id and token:
                    return True
                else:
                    return False

            # VERIFICA SE O RETORNO FOI DIFERENTE DE CRIAÇÃO E SOLICITAÇÃO DOS DADOS
            # MAS SE O DISPOSITIVO JÁ TIVER OS DADOS NECESSARIOS O LOOP E ENCERRADO
            elif not auto_register.response_status_code() in [self.const.HTTPResponse.CREATED,
                                                              self.const.HTTPResponse.OK,
                                                              self.const.HTTPResponse.UNAUTHORIZED]:
                email = self.config.load_register('api_user', None, False)
                password = self.config.load_register('api_pass', None, False)
                device_id = self.config.load_register('api_pass', None, False)
                token = self.config.load_register('token', None, False)

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
        try:
            # Solicitar hora do servidor NTP
            ntptime.settime()

            # Ajustar para o fuso horário de Brasília (UTC-3)
            (year, month, day, weekday, hour, minute, second, millisecond) = self.rtc.datetime()
            hour = (hour - 3) % 24  # ajusta para UTC-3
            self.rtc.datetime((year, month, day, weekday, hour, minute, second, millisecond))

            print("Tempo sincronizado:", rtc.datetime())
        except Exception as e:
            print("Erro ao sincronizar o tempo:", e)

    def current_datetime(self):
        current_datetime = self.rtc.datetime()
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            current_datetime[0], current_datetime[1], current_datetime[2],
            current_datetime[4], current_datetime[5], current_datetime[6]
        )

    def get_current_date_only(self):
        current_datetime = self.rtc.datetime()
        return "{:04d}-{:02d}-{:02d}".format(
            current_datetime[0], current_datetime[1], current_datetime[2]
        )

    def get_current_time_only(self):
        current_datetime = self.rtc.datetime()
        return "{:02d}:{:02d}:{:02d}".format(
            current_datetime[4], current_datetime[5], current_datetime[6]
        )

    # verificar se tem comandos a serem executados
    def get_command(self):
        command_request = ZDCRequest()
        response = command_request.execute_method(f"/devices/command/{self.id}", "GET", None, False)
        if command_request.response_status_code() == self.const.HTTPResponse.OK:
            return self.command.execute_command(response.get('command'))
        else:
            return None

    def login(self):
        email = self.config.load_register('api_user')
        password = self.config.load_register('api_pass')
        request_login = ZDCRequest()
        data = {'email': email, 'password': password, 'module': "ZDAC-ESP"}
        response = request_login.execute_method(f"/users/login", "POST", data, False)
        if request_login.response_status_code() == self.const.HTTPResponse.OK:
            self.config.save_register('token', response.get('token'))
            return True
        else:
            print(response.get('message'))
            return False
