from stem import Signal
from stem.control import Controller
import requests

class Comms(object):
    def __init__(self, *args, **kwargs):
        self.session = requests.session()
        # Tor uses 9051 as the default Control Port
        self.control_port = 9151
        self.control_password = "test"
        # Tor uses the 9050 port as the default socks port
        self.session.proxies = {
            'http':  'socks5://localhost:9050',
            'https': 'socks5://localhost:9050'
        }
        self.test_url = "http://httpbin.org/ip"
        self.always_refresh = False
        self.refresh_session()  # ALWAYS DO THIS ON INIT????? TODO: is this right?

    def refresh_session(self):
        with Controller.from_port(port = self.control_port) as controller:
            controller.authenticate(password=self.control_password)
            controller.signal(Signal.NEWNYM)
    
    def reset(self): self.refresh_session()

    def __call__(self, addr):
        # try to make the request
        try:
            data = self.session.get(addr)
        except Exception as e:
            data = e

        if self.always_refresh:
            self.refresh_session()
        
        return data

    def __test__(self):
        return self.__call__(self.test_url).text


if __name__ == "__main__":
    app = Comms()
    print(f"Working IP: {app.__test__()}")
