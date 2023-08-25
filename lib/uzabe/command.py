from lib.uzabe.requests import ZDCRequest
from lib.uzabe.configs import ZDCConfig
import machine
import mip


class ZDCCommand:
    def __init__(self):
        self.config = ZDCConfig()
        self.device_id = self.config.load_register('id') or self.config.load_register('mac')
        self.COMMANDS = {
            "update": self.update,
            "reboot": self.reboot,
            "request_token": self.request_token,
            "reset": self.reset
        }

    def update(self):
        # comandos serão executados aqui
        if self.request_removal_of_command("update"):
            print("Update command executed.")
            return True
        return False

    def reboot(self):
        # comandos serão executados aqui
        if self.request_removal_of_command("reboot"):
            print("Reboot command executed.")
            return True
        return False

    def reset(self):
        # comandos serão executados aqui
        if self.request_removal_of_command("reset"):
            print("Reset command executed.")
            return True
        return False

    def request_token(self):
        # comandos serão executados aqui
        if self.request_removal_of_command("request_token"):
            print("Request token command executed.")
            return True
        return False

    def request_removal_of_command(self, command_name):
        request_command = ZDCRequest()
        data = {'device_id': self.device_id, 'command_name': command_name}
        response = request_command.execute_method("/devices/command", "DELETE", data)

        if response and response.get('status') == 'success':
            return True
        return False

    def execute_command(self, command_name):
        if command_name in self.COMMANDS:
            function_to_execute = self.COMMANDS[command_name]
            success = function_to_execute()
            if success:
                machine.reset()

