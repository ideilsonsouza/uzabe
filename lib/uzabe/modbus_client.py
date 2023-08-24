import socket


class ZDCModbus:
    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.sock = None
        self._transaction_id = 0

    def connect(self):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    @property
    def transaction_id(self):
        tid = self._transaction_id
        self._transaction_id = (self._transaction_id + 1) % 0xFFFF
        return tid.to_bytes(2, 'big')

    def read_holding_registers(self, address, count, unit):
        protocol_id = b'\x00\x00'
        length = b'\x00\x06'
        unit_id = unit.to_bytes(1, 'big')
        function_code = b'\x03'
        starting_address = address.to_bytes(2,'big')
        quantity = count.to_bytes(2, 'big')

        request = self.transaction_id + protocol_id + length + unit_id + function_code + starting_address + quantity
        self.sock.send(request)
        response = self.sock.recv(1024)
        byte_count = response[8]
        values = [int.from_bytes(response[9 + i*2:11 + i*2], 'big') for i in range(byte_count // 2)]
        return values
    
    def read_float_registers(self, address, count, unit):
        protocol_id = b'\x00\x00'
        length = b'\x00\x06'
        unit_id = unit.to_bytes(1, 'big')
        function_code = b'\x03'  # Código de função para registros de holding
        starting_address = address.to_bytes(2,'big')
        quantity = (count * 2).to_bytes(2, 'big')  # Contamos pares de registros

        request = self.transaction_id + protocol_id + length + unit_id + function_code + starting_address + quantity
        self.sock.send(request)
        response = self.sock.recv(1024)
        byte_count = response[8]
    
        float_values = []
        
        for i in range(0, byte_count, 4):
            float_bytes = response[9 + i:13 + i]
            float_value = struct.unpack('>f', float_bytes)[0]
            float_values.append(float_value)
        
        return float_values
