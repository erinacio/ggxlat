import requests

FAKE_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'

def make_session():
    session = requests.Session()
    session.headers.update({'User-Agent': FAKE_UA})
    return session
