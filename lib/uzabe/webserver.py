from lib.umicrowebserver.microWebSrv import MicroWebSrv
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.device import ZDCDevice

import machine

network = ZDCNetwork()
config = ZDCConfig()
device = ZDCDevice()

@MicroWebSrv.route('/')
def _index(http_client, http_response):
    http_response.WriteResponseFile("www/login.html", contentType="text/html")

@MicroWebSrv.route('/login')
def _login(http_client, http_response):
    http_response.WriteResponseFile("www/login.html", contentType="text/html")

@MicroWebSrv.route('/dashboard')
def _dashboard(http_client, http_response):
    http_response.WriteResponseFile("www/dashboard.html", contentType="text/html")


@MicroWebSrv.route('/config')
def _config(http_client, http_response):
    http_response.WriteResponseFile("www/config.html", contentType="text/html")


@MicroWebSrv.route('/info')
def _info(http_client, http_response):
    http_response.WriteResponseFile("www/info.html", contentType="text/html")


@MicroWebSrv.route('/device-info')
def _device_info(http_client, http_response):
    mac_wlan = network.get_wlan_mac()
    mac_lan = network.get_lan_mac()
    ip_wlan = network.get_wlan_ip()
    ip_lan = network.get_lan_ip()
    last_change = config.load_register('last_change')
    saved_ssid = config.load_register('ssid')
    url_server = config.load_register('url_server')
    device_name = config.load_register('name')

    data = {
        'mac_wlan': mac_wlan,
        'mac_lan': mac_lan,
        'ip_wlan': ip_wlan,
        'ip_lan': ip_lan,
        'last_change': last_change,
        'saved_ssid': saved_ssid,
        'url_server': url_server,
        'device_name': device_name
    }

    http_response.WriteResponseJSONOk(data)


@MicroWebSrv.route('/login', 'POST')
def _post_login(http_client, http_response):
    form_data: dict = http_client.ReadRequestPostedFormData()
    username = form_data["username"]
    password = form_data["password"]

    if username == "admin" and password == "admin":
        http_response.WriteResponseRedirect('/dashboard')
    else:
        http_response.WriteResponseRedirect('/login')


@MicroWebSrv.route('/reset-settings', 'POST')
def _post_reset_settings(http_client, http_response):
    url_server = config.load_register('url_server')
    ssid_pass = config.load_register('ssid_pass')
    ssid = config.load_register('ssid')
    if url_server and ssid_pass and ssid:
        config.save_register('isConfigured', True)
        http_response.WriteResponseRedirect('/info')


@MicroWebSrv.route('/reboot-device', 'POST')
def _post_reboot_device(http_client, http_response):
    machine.reset()

@MicroWebSrv.route('/desable-settings', 'POST')
def _post_desable_settings(http_client, http_response):
    url_server = config.load_register('url_server')
    ssid_pass = config.load_register('ssid_pass')
    ssid = config.load_register('ssid')
    if url_server and ssid_pass and ssid:
        config.save_register('isConfigured', True)
        http_response.WriteResponseRedirect('/info')


@MicroWebSrv.route('/set-config', 'POST')
def _post_set_config(http_client, http_response):
    form_data = http_client.ReadRequestPostedFormData()

    ssid = form_data.get("ssid", "").strip()
    wifi_password = form_data.get("ssid_pass", "").strip()
    url_server = form_data.get("url_server", "").strip()
    device_desc = form_data.get("description", "").strip()

    if ssid:
        config.save_register('ssid', ssid)
        if wifi_password:
            config.save_register('ssid_pass', wifi_password)
            if url_server:
                data_format = device.current_datetime()
                config.save_register('url_server', url_server)
                config.save_register('last_change', data_format)
                config.save_register('description', device_desc)
                http_response.WriteResponseRedirect('/info', contentType="text/html")



def _acceptWebSocketCallback(webSocket, httpClient):
    print("WS ACCEPT")
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback


def _recvTextCallback(webSocket, msg):
    print("WS RECV TEXT : %s" % msg)
    webSocket.SendText("Reply for %s" % msg)


def _recvBinaryCallback(webSocket, data):
    print("WS RECV DATA : %s" % data)


def _closedCallback(webSocket):
    print("WS CLOSED")


def start_server():
    srv = MicroWebSrv(webPath='www/')
    srv.MaxWebSocketRecvLen = 256
    srv.WebSocketThreaded = True
    srv.AcceptWebSocketCallback = _acceptWebSocketCallback
    srv.Start()


