import network as sys_network
import ubinascii as binascii
import socket
import os
import time
from lib.uzabe.configs import ZDCConfig

class ZDCNetwork:
    def __init__(self):
        self.config = ZDCConfig()

    @staticmethod
    def ping_domain(url, port=80, timeout=5):
        domain = url.split("://")[-1].split("/")[0]
        try:
            addr_info = socket.getaddrinfo(domain, port)
            addr = addr_info[0][-1]

            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)
            s.close()
            return True
        except OSError:
            return False

    @staticmethod
    def is_host_reachable(ip, port=80):
        try:
            addr_info = socket.getaddrinfo(ip, port)
            addr = addr_info[0][-1]

            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)
            s.close()
            return True
        except OSError:
            return False

    @staticmethod
    def simple_ping(host, port=502, timeout=5):
        addr = socket.getaddrinfo(host, port)[0][-1]

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        s.settimeout(timeout)

        try:
            s.sendto('PING', addr)

            data, addr = s.recvfrom(1024)
            if data == b'PONG':
                return True
            return False
        except OSError:
            return False
        finally:
            s.close()

    @staticmethod
    def connect_wifi(ssid, password):
        wlan = sys_network.WLAN(sys_network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                time.sleep(1)

    def connect_to_wifi(self):
        timeout = 10
        sys_credentials = ZDCConfig()
        wifi_name = self.config.load_register('ssid')
        wifi_password = self.config.load_register('ssid_pass')
        self.stop_client_ap()
        wlan = sys_network.WLAN(sys_network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(wifi_name, wifi_password)

            start_time = time.time()
            while not wlan.isconnected():
                if time.time() - start_time > timeout:
                    return False
                time.sleep(1)

        return True

    def start_client_ap(self):
        wifi_ap_name = self.config.load_register('ap_ssid')
        wifi_ap_password = self.config.load_register('ap_pass')
        sta_if = sys_network.WLAN(sys_network.STA_IF)
        if sta_if.active():
            sta_if.active(False)

        ap_if = sys_network.WLAN(sys_network.AP_IF)
        ap_if.active(True)

        ap_if.config(essid=wifi_ap_name, password=wifi_ap_password)

    @staticmethod
    def stop_client_ap():
        ap_if = sys_network.WLAN(sys_network.AP_IF)

        if ap_if.active():
            ap_if.active(False)

    def get_network_mac(self):
        mac = binascii.hexlify(sys_network.WLAN().config('mac'), ':').decode()
        return mac

    def get_network_ip(self):
        wlan = sys_network.WLAN(sys_network.STA_IF)
        ifconfig = wlan.ifconfig()
        return ifconfig[0]

