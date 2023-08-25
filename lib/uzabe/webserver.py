from lib.umicrowebserver.microWebSrv import MicroWebSrv
from lib.uzabe.network import ZDCNetwork
from lib.uzabe.configs import ZDCConfig
from lib.uzabe.device import ZDCDevice

credentials = ZDCConfig()

class ZDCWebServer:
    def __init__(self):
        self.srv = MicroWebSrv(webPath='www/')
        self.config = ZDCConfig()
        self.network = ZDCNetwork()
        self.device = ZDCDevice()

    @MicroWebSrv.route('/')
    def _index(self, http_client, http_response):
        http_response.WriteResponseFile("/www/login.html", contentType="text/html")

    @MicroWebSrv.route('/login')
    def _login(self, http_client, http_response):
        http_response.WriteResponseFile("/www/login.html", contentType="text/html")

    @MicroWebSrv.route('/dashboard')
    def _dashboard(self, http_client, http_response):
        http_response.WriteResponseFile("/www/dashboard.html", contentType="text/html")

    @MicroWebSrv.route('/config')
    def _config(self, http_client, http_response):
        http_response.WriteResponseFile("/www/config.html", contentType="text/html")

    @MicroWebSrv.route('/info')
    def _info(self, http_client, http_response):
        http_response.WriteResponseFile("/www/info.html", contentType="text/html")

    @MicroWebSrv.route('/device_info')
    def _device_info(self, http_client, http_response):
        mac_wlan = self.network.get_wlan_mac()
        mac_lan = self.network.get_lan_mac()
        ip_wlan = self.network.get_wlan_ip()
        ip_lan = self.network.get_lan_ip()
        last_change = self.config.load_register('last_change')
        saved_ssid = self.config.load_register('ssid')
        url_server = self.config.load_register('url_server')

        data = {
            'mac_wlan': mac_wlan,
            'mac_lan': mac_lan,
            'ip_wlan': ip_wlan,
            'ip_lan': ip_lan,
            'last_change': last_change,
            'saved_ssid': saved_ssid,
            'url_server': url_server
        }

        http_response.WriteResponseJSONOk(data)

    @MicroWebSrv.route('/login', 'POST')
    def _post_login(self, http_client, http_response):
        form_data: dict = http_client.ReadRequestPostedFormData()
        username = form_data["username"]
        password = form_data["password"]

        if username == "admin" and password == "admin":
            http_response.WriteResponseRedirect('/dashboard')
        else:
            http_response.WriteResponseRedirect('/login')

    @MicroWebSrv.route('/reset_settings', 'POST')
    def _post_reset_settings(self, http_client, http_response):

        print("Solicitado a remoção do arquivo de credenciais")

    @MicroWebSrv.route('/reboot_device', 'POST')
    def _post_reboot_device(self, http_client, http_response):
        machine.reset()

    @MicroWebSrv.route('/set_config', 'POST')
    def _post_set_config(self, http_client, http_response):
        form_data = http_client.ReadRequestPostedFormData()

        ssid = form_data.get("ssid", "").strip()
        wifi_password = form_data.get("password", "").strip()
        url_server = form_data.get("url_server", "").strip()

        if ssid:
            credentials.save_register('ssid', ssid)
            if wifi_password:
                credentials.save_register('ssid_pass', wifi_password)
                if url_server:
                    data_format = self.device.current_datetime()
                    credentials.save_register('url_server', url_server)
                    credentials.save_register('isConfigured', True)
                    credentials.save_register('last_change', data_format)

        http_response.WriteResponseRedirect('/success')

        self.stop_server()
        machine.reset()

    @MicroWebSrv.route('/success')
    def _response_success(self, http_response):
        content = ("\\n"
                   "        <!DOCTYPE html>\n"
                   "        <html lang=en>\n"
                   "            <head>\n"
                   "                <meta charset=\"UTF-8\" />\n"
                   "                <title>Success</title>\n"
                   "            </head>\n"
                   "            <body>\n"
                   "                <h1>Configuration Saved Successfully!</h1>\n"
                   "                <h2>device is being restarted</h2>\n"
                   "            </body>\n"
                   "        </html>\n"
                   "        ")
        http_response.WriteResponseOk(headers=None,
                                     contentType="text/html",
                                     contentCharset="UTF-8",
                                     content=content)

    def start_server(self):
        self.srv.Start()

    def stop_server(self):
        self.srv.Stop()
