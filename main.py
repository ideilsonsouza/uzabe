import machine
import time
from zdc_network import ZDCNetwork
from zdc_device import ZDCDevice
from zdc_credentials import ZDCCredentials

MAX_RETRIES = 3
MAX_TENTATIVE_LOGIN = 20
TIMEOUT = 30


class ZDCApplication:

    def __init__(self):
        self.execute_counter = 0
        self.time_loop = 20
        self.sys_credentials = ZDCCredentials()
        self.sys_device = ZDCDevice()
        self.sys_network = ZDCNetwork()

    def get_datasource(self):
        # TODO: Implementar este método
        pass

    def send_datavalues(self):
        # TODO: Implementar este método
        pass

    def check_command(self):
        # TODO: Implementar este método
        pass

    def execute_command(self):
        # TODO: Implementar este método
        pass

    def login(self):
        user_connected = self.sys_device.login()
        while not user_connected and self.execute_counter < MAX_TENTATIVE_LOGIN:
            self.execute_counter += 1
            time.sleep(TIMEOUT)
            user_connected = self.sys_device.login()
        return user_connected

    def run(self):
        if not self.login():
            if self.execute_counter >= MAX_TENTATIVE_LOGIN:
                raise Exception("Max login attempts reached")

        while True:
            self.time_loop = self.fetch_time_loop()

            if not self.check_command():
                if self.get_datasource():
                   if self.send_datavalues():
                       print("Não foi encontrado valores de dados a serem enviado")
                    else:
                        pass

            else:
                print("Exite comandos a ser executados")
                self.execute_command()

            time.sleep(self.time_loop)

    def fetch_time_loop(self):
        return int(self.sys_credentials.load_register('time_loop', default='20'))


if __name__ == "__main__":
    app = ZDCApplication()
    while True:
        try:
            app.run()
        except Exception as e:
            print(f"Erro: {e}. Reiniciando o dispositivo...")
            machine.reset()
