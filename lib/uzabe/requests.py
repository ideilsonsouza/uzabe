import urequests as urequest
import ujson
from lib.uzabe.configs import ZDCConfig

class ZDCRequest:
    def __init__(self, method="GET"):
        self.config = ZDCConfig()
        self.base_url = self.config.load_register('url_server', 'http://www.zabe.com.br/').rstrip('/')
        self.token = self.config.load_register('token', '')
        self.method = method
        self._last_response = None

    def _get_headers(self, is_json=True, include_token=True):
        """Return the necessary headers for the request."""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'ZDAC ESP32/1.0',
            'Content-Type': 'application/json; charset=utf-8' if is_json else 'charset=utf-8'
        }

        if include_token and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        return headers

    def _build_full_url(self, path):
        """Construct the full URL for the request."""
        return f"{self.base_url}/api/{path.lstrip('/')}"

    def _decode_utf8(self, response):
        """Decode response content."""
        try:
            return response.content.decode('utf-8')
        except AttributeError:
            return response

    def _execute_request(self, method, url, data=None, include_token=True):
        """General method to execute a request and handle the response."""
        headers = self._get_headers(is_json=bool(data), include_token=include_token)
        response = None
        try:
            if method == "GET":
                response = urequest.get(url, data=ujson.dumps(data) if data else None, headers=headers)
            elif method in ["POST", "PUT"]:
                response = getattr(urequest, method.lower())(url, data=ujson.dumps(data), headers=headers)
            elif method == "DELETE":
                response = urequest.delete(url, headers=headers)

            self._last_response = response
            response_text = self._decode_utf8(response)
            return ujson.loads(response_text)
        except Exception as e:
            print(f"Error executing {method} request: {e}")
            return None

    def execute_method(self, path, method="GET", data=None, include_token=True):
        """Execute a specific HTTP method."""
        method = method or self.method
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported method: {method}")

        print(self._build_full_url(path))
        return self._execute_request(method, self._build_full_url(path), data=data, include_token=include_token)

    def response_status_code(self):
        """Get the status code from the last response."""
        if self._last_response is None:
            return None
        return self._last_response.status_code
