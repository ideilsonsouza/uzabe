import machine
import time
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.device import ZDCDevice
import lib.uzabe.webserver as webserver


MAX_RETRIES = 3
TIMEOUT = 20

class ZDCSystem:
    reboot_counter = 0

    def __init__(self):
        self.config = ZDCConfig()
        self.device = ZDCDevice()
        self.network = ZDCNetwork()
        self.sys_user = 'emRhY0B6YWJlLmNvbS5icg=='
        self.sys_pass = 'WmRhY2VzcA=='
        self.time_loop = 'MjA='        
        lac_mac = self.network.get_lan_mac()
        wlan_mac = self.network.get_wlan_mac()
        mac = wlan_mac.replace(':', '').upper() or lac_mac.replace(':', '').upper()
        self.device_name = f"ZDC-{mac}"
        self.wifi_ap_name = self.device_name
        self.wifi_ap_password = '@12345678'
        self.rtc = machine.RTC()
        self.isConfigured = self.config.load_register('isConfigured', decode=False)

    def _save_system_register(self):
        try:
            self.config.save_register('sys_user', self.sys_user, encode=False)
            self.config.save_register('sys_pass', self.sys_pass, encode=False)
            self.config.save_register('time_loop', self.time_loop, encode=False)
            self.config.save_register('name', self.device_name, encode=True)
            self.config.save_register('ap_ssid', self.wifi_ap_name, encode=True)
            self.config.save_register('ap_pass', self.wifi_ap_password, encode=True)
            return True

        except ValueError as e:
            print(f"Falha ao tentar salvar os registros: \
            {e}")

    def login(self):
        user_connected = self.device.login()
        ZDCSystem.reboot_counter = 0
        while not user_connected and ZDCSystem.reboot_counter < MAX_RETRIES:
            ZDCSystem.reboot_counter += 1
            time.sleep(TIMEOUT)
            user_connected = self.device.login()
        return user_connected

    def start_system_device(self):
        # salvar as variaveis padrão do sistema
        if self._save_system_register():
            print(f"Credenciais salvas com sucesso")

        ZDCSystem.reboot_counter = 0
        #verifica se o dispositivo já foi configurado
        if not self.isConfigured:
            # se o dispositivo nunca foi configurado ele é iniciado no modo ap com um servidor web
            self.network.start_client_ap()
            webserver.start_server()
        else:
            # mas se caso o dispositivo já foi configurado le vai tentar se conectar a rede wifi
            ty_connect_wifi = self.network.connect_to_wifi()
            ZDCSystem.reboot_counter = 0

            # o dispositivo ira permanecer no loop ate que se connect a rede wifi
            while not ty_connect_wifi and ZDCSystem.reboot_counter < MAX_RETRIES:
                ZDCSystem.reboot_counter += 1
                print(f"{ZDCSystem.reboot_counter}º Tentativa de conexão com Wifi")
                time.sleep(TIMEOUT)
                ty_connect_wifi = self.network.connect_to_wifi()

            # se o dispositivo conseguir se conectar a rede wifi
            if ty_connect_wifi:
                print(f"Rede {self.config.load_register('ssid')} -> Conectada")
                # é verificado se o dispositivo já tem o seu id
                device_id = self.config.load_register('id')
                server_base_url = self.config.load_register('url_server')

                # se o dispositivo não tiver um id é iniciado o processo de validação
                if not device_id:
                    # primeira tentativa é se conectar com o servidor, fazendo um ping
                    ty_ping_server = self.network.ping_domain(server_base_url)
                    ZDCSystem.reboot_counter = 0

                    # se o servidor não responder a solicitação o loop continua ate que o mesmo responda
                    while not ty_ping_server and ZDCSystem.reboot_counter < MAX_RETRIES:
                        ZDCSystem.reboot_counter += 1
                        print(f"{ZDCSystem.reboot_counter}º Tentativa de conexão com servidor")
                        time.sleep(TIMEOUT)
                        ty_ping_server = self.network.ping_domain(server_base_url)

                    # se ouver uma resposta do servidor inicia o processo de auto registro
                    # o dispositivo deve permanecer neste loop ate que seja configurado no servidor
                    if ty_ping_server:
                        # tentativas de se registrar e obter as configuraçõe no servidor
                        ty_registration_server = self.device.apply_for_registration
                        ZDCSystem.reboot_counter = 0

                        while not ty_registration_server and ZDCSystem.reboot_counter < MAX_RETRIES:
                            ZDCSystem.reboot_counter += 1
                            print(f"{ZDCSystem.reboot_counter}º Tentativa de conexão com servidor")
                            time.sleep(TIMEOUT)
                            ty_registration_server = self.device.apply_for_registration

                        if ty_registration_server:
                            return True
                    else:
                        return False

                # se o dispositivo já tem um id
                else:
                    # e verificado se o dispositivo ainda não tem um token
                    device_token = self.config.load_register('token')
                    ZDCSystem.reboot_counter = 0

                    if device_token:
                        return True
                    else:
                        if self.login():
                            return True
