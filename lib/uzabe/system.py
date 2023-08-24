import machine
import time
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.webserver import ZDCWebServer
from lib.uzabe.device import ZDCDevice
from lib.uzabe.configs import ZDCConfig


MAX_RETRIES = 3
TIMEOUT = 20

sys_device = ZDCDevice()
sys_network = ZDCNetwork()
sys_credentials = ZDCConfig()
sys_webserver = ZDCWebServer()


class ZDCSystem:
    _config = ZDCConfig()
    _count = 0

    def __init__(self):
        self.sys_user = 'emRhY0B6YWJlLmNvbS5icg=='
        self.sys_pass = 'WmRhY2VzcA=='
        self.time_loop = 'MjA='        
        mac = sys_network.get_network_mac().replace(':', '').upper()
        self.device_name = f"ZDC-{mac}"
        self.wifi_ap_name = self.device_name
        self.wifi_ap_password = '@12345678'
        self.rtc = machine.RTC()
        self.device_configured = self._config.load_register('device_configured', decode=False)

    def _save_system_register(self):
        try:
            self._config.save_register('admin_user', self.sys_user, encode=False)
            self._config.save_register('admin_pass', self.sys_pass, encode=False)
            self._config.save_register('time_loop', self.time_loop, encode=False)
            self._config.save_register('device_name', self.device_name, encode=True)
            self._config.save_register('ap_name', self.wifi_ap_name, encode=True)
            self._config.save_register('ap_pass', self.wifi_ap_password, encode=True)
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
        if self.device_configured:
            ty_connect = sys_network.connect_to_wifi()
            if ty_connect:
                return True

            while not ty_connect and ZDCSystem.reboot_counter < MAX_RETRIES:
                ZDCSystem.reboot_counter += 1
                print(f"Tentativa de conexão com Wifi{ZDCSystem.reboot_counter}")
                time.sleep(TIMEOUT)
                connected_wifi = sys_network.connect_to_wifi()

            if ZDCSystem.reboot_counter >= MAX_RETRIES:
                return False

        else:
            print(f"Iniciando sistema de configuração")
            sys_network.start_client_ap()
            sys_webserver.start_server()
            return False

    def start_system_device(self):
        if not self.try_function(self.start_system_network, "Tentativa de conexão com Wifi"):
            return False

        print(f"Rede {sys_credentials.get_credentials('wifi_name')} -> Conectada")

        server_base_url = sys_credentials.get_credentials('base_url')
        if not self.try_function(lambda: sys_network.ping_domain(server_base_url),
                                 f"Tentativa de conexão com servidor {server_base_url}"):
            return False

        if not self.try_function(sys_device.register_on_server, "Tentativa de se auto registrar"):
            return False

        if not self.try_function(sys_device.get_user, "Tentativa de se auto registrar"):
            return False

        return True
