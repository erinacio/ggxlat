import re
from datetime import datetime
from .requtils import make_session
from .ggmagic import sM

RE_TKK = re.compile(r"TKK=eval\('\(\(function\(\){(.*?)}\)\(\)\)'\);")
RE_TKK_BODY = re.compile(r"var\ a\=(.+?)\;var\ b\=(.+?)\;return\ (.+?)\+\'\.\'\+\(a\+b\)")
DT_ZERO = datetime(1970, 1, 1, 0, 0, 0)


class GGTokenError(Exception):
    pass

def hour_now():
    span = datetime.utcnow() - DT_ZERO
    return span.days * 24 + span.seconds // 3600


def resolve_tkk(tkk):
    matcher = RE_TKK_BODY.match(tkk)
    if matcher is None:
        raise GGTokenError('Unexpected TKK {}'.format(tkk))
    a = int(matcher.group(1))
    b = int(matcher.group(2))
    prefix = matcher.group(3)
    return '{}.{}'.format(prefix, a + b)


class TokenGetter:
    def __init__(self, domain='translate.google.cn', token=None):
        self._session = make_session()
        self._domain = domain
        self._token = token
        self._token_hour = 0 if token is None else int(token.split('.')[0])

    def refresh_token(self):
        '''Get a new token if the old one is outdated'''
        hour = hour_now()
        if hour != self._token_hour:
            r = self._session.get('https://{}/'.format(self._domain))
            if r.status_code != 200:
                raise GGTokenError('Refreshing token, request got {}'.format(r.status_code))
            found = RE_TKK.search(r.text)
            tkk = found.group(1).encode().decode('unicode_escape')
            self._token = resolve_tkk(tkk)
            self._token_hour = hour

    def get_token(self, text):
        '''Get the request token for translating the given text'''
        self.refresh_token()
        return sM(text, self._token)

    @classmethod
    def try_reload(cls, cached_path):
        try:
            with open(cached_path) as fp:
                token = fp.read().strip()
                if re.fullmatch(r'\d+\.\d+', token) is None:
                    token = None
        except IOError:
            token = None

        return TokenGetter(token=token)

    def save_to(self, cached_path):
        with open(cached_path, 'w') as fp:
            print(self._token, file=fp)
