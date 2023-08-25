import machine
import time
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.webserver import ZDCWebServer
from lib.uzabe.device import ZDCDevice


MAX_RETRIES = 3
TIMEOUT = 20

class ZDCSystem:
    _count = 0

    def __init__(self):
        self.config = ZDCConfig()
        self.device = ZDCDevice()
        self.network = ZDCNetwork()
        self.webserver = ZDCWebServer()
        self.sys_user = 'emRhY0B6YWJlLmNvbS5icg=='
        self.sys_pass = 'WmRhY2VzcA=='
        self.time_loop = 'MjA='        
        mac = self.network.get_network_mac().replace(':', '').upper()
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

    def try_function(self, function, message, retries=MAX_RETRIES):
        success = function()
        while not success and self._count < retries:
            self._count += 1
            print(f"{message} - Tentativa {self._count}")
            time.sleep(TIMEOUT)
            success = function()

        return success

    def network_connect(self):
        if self._save_system_register():
            print(f"Credenciais salvas com sucesso")

        ZDCSystem.reboot_counter = 0
        if self.isConfigured:
            ty_connect = self.network.connect_to_wifi()
            if ty_connect:
                return True

            while not ty_connect and ZDCSystem.reboot_counter < MAX_RETRIES:
                ZDCSystem.reboot_counter += 1
                print(f"{ZDCSystem.reboot_counter}º Tentativa de conexão com Wifi")
                time.sleep(TIMEOUT)
                ty_connect = self.network.connect_to_wifi()

            if ZDCSystem.reboot_counter >= MAX_RETRIES:
                return False

        else:
            print(f"Iniciando sistema de configuração")
            if self.network.start_client_ap():
                self.webserver.start_server()
            return False

    def start_system_device(self):
        if not self.try_function(self.network_connect, "Tentativa de conexão com Wifi"):
            return False

        print(f"Rede {self.config.load_register('ssid')} -> Conectada")

        server_base_url = self.config.load_register('url_server')
        if not self.try_function(lambda: self.network.ping_domain(server_base_url),
                                 f"Tentativa de conexão com servidor {server_base_url}"):
            return False

        if not self.try_function(self.device.apply_for_registration, "Tentativa de validar o acesso"):
            return False

        return True
