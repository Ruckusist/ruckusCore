from stem import Signal
from stem.control import Controller
import requests

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://localhost:9050',
                       'https': 'socks5://localhost:9050'}
    return session

# signal TOR for a new connection 
def renew_connection():
    # THIS IS NOT WORKING.
    with Controller.from_port(port = 9151) as controller:
        controller.authenticate(password="test")
        controller.signal(Signal.NEWNYM)
# renew_connection()

def test():
    session = get_tor_session()
    test_url = "http://httpbin.org/ip"
    tor_ip = ""
    try:
        tor_ip = session.get(test_url).text
        # tor_ip = session.get("https://ruckusist.com").text
    except Exception as e:
        print("Tor failing.")
        print(e)
        pass

    # Following prints your normal public IP
    my_ip = requests.get(test_url).text
    
    print(f"MY IP: {my_ip}  | TOR IP: {tor_ip}")
    return session

test()
renew_connection()
test()