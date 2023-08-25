import machine
from MicroWebSrv.microWebSrv import MicroWebSrv
from uzconfigs import ZDCCredentials
from uznetwork import ZDCNetwork

credentials = ZDCCredentials()
networks = ZDCNetwork()

srv = MicroWebSrv(webPath='www/')

class ZDCWebServer:

    @MicroWebSrv.route('/')
    def _httpHandlerIndex(httpClient, httpResponse):
        httpResponse.WriteResponseFile("/www/login.html", contentType="text/html")

    @MicroWebSrv.route('/login')
    def _httpHandlerLogin(httpClient, httpResponse):
        httpResponse.WriteResponseFile("/www/login.html", contentType="text/html")

    @MicroWebSrv.route('/dashboard')
    def _httpHandlerDashboard(httpClient, httpResponse):
        httpResponse.WriteResponseFile("/www/dashboard.html", contentType="text/html")

    @MicroWebSrv.route('/config')
    def _httpHandlerConfig(httpClient, httpResponse):
        httpResponse.WriteResponseFile("/www/config.html", contentType="text/html")

    @MicroWebSrv.route('/info')
    def _httpHandlerInfo(httpClient, httpResponse):
        httpResponse.WriteResponseFile("/www/info.html", contentType="text/html")

    @MicroWebSrv.route('/device_info')
    def _httpHandlerDeviceInfo(httpClient, httpResponse):
        mac_address = networks.get_network_mac()
        last_change = ZDCCredentials.load_register('last_change')
        saved_ssid = ZDCCredentials.load_register('wifi_name')

        data = {
            'mac_address': mac_address,
            'last_change': last_change,
            'saved_ssid': saved_ssid
        }

        httpResponse.WriteResponseJSONOk(data)


    @MicroWebSrv.route('/login', 'POST')
    def _httpHandlerCheckLogin(httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()
        username = formData["username"]
        password = formData["password"]

        if username == "admin" and password == "admin":
            httpResponse.WriteResponseRedirect('/dashboard')
        else:
            httpResponse.WriteResponseRedirect('/login')


    @MicroWebSrv.route('/reset_settings', 'POST')
    def _httpHandlerSaveWifiReset_settings(httpClient, httpResponse):

        print("Solicitado a remoção do arquivo de credenciais")


    @MicroWebSrv.route('/reboot_device', 'POST')
    def _httpHandlerSaveWifiReboot_device(httpClient, httpResponse):
        machine.reset()

    @MicroWebSrv.route('/set_config', 'POST')
    def _httpHandlerSaveWifiConfig(httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()

        ssid = formData.get("ssid", "").strip()
        wifi_password = formData.get("password", "").strip()
        base_url = formData.get("base_url", "").strip()

        if ssid:
            credentials.save_register('wifi_name', ssid)
            if wifi_password:
                credentials.save_register('wifi_password', wifi_password)
                if base_url:
                    credentials.save_register('base_url', base_url)
                    credentials.save_register('device_configured', True)


        httpResponse.WriteResponseRedirect('/success-page')

        ZDCWebServer.stop_server()
        machine.reset()


    @MicroWebSrv.route('/success-page')
    def _httpHandlerSuccessPage(httpClient, httpResponse):
        content = """\
        <!DOCTYPE html>
        <html lang=en>
            <head>
                <meta charset="UTF-8" />
                <title>Success</title>
            </head>
            <body>
                <h1>Configuration Saved Successfully!</h1>
            </body>
        </html>
        """
        httpResponse.WriteResponseOk(headers=None,
                                     contentType="text/html",
                                     contentCharset="UTF-8",
                                     content=content)

    @staticmethod
    def start_server():
        srv.Start()

    @staticmethod
    def stop_server():
        srv.Stop()
   