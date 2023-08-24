from modbus_client import ZDCModbus

class ModbusDevice:
    def __init__(self, host):
        self.client = ZDCModbus(host)

    def connect(self):
        self.client.connect()

    def read_value(self, address, count, unit):
        return self.client.read_holding_registers(address, count, unit)
    
    def read_float_values(self, address, count, unit):
        return self.client.read_float_registers(address, count, unit)
    
    def close(self):
        self.client.close()
