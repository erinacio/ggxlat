import json

from .requtils import make_session
from .ggtoken import TokenGetter


class GGXlatError(Exception): pass


def make_params(from_lang, to_lang, token, text):
    params = {
            'client': 't',
            'sl': from_lang,
            'tl': to_lang,
            'hl': to_lang,
            'tk': token,
            'dt': ['at', 'bd', 'ex', 'ld', 'md', 'qca', 'rw', 'rm', 'ss', 't'],
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'otf': '1',
            'ssel': '0',
            'tsel': '0',
            'kc': '7',
            'q': text,
            }
    return params


class Translator:
    def __init__(self, token_getter=None, domain='translate.google.cn', from_lang='auto', to_lang='zh_CN', dict_mode=False):
        if token_getter is None:
            token_getter = TokenGetter()
        if type(token_getter) is not TokenGetter:
            raise TypeError('Expected {}, {} got', TokenGetter, type(token_getter))
        self._token_getter = token_getter
        self._domain = domain
        self._from = from_lang
        self._to = to_lang
        self._dict_mode = dict_mode
        self._session = make_session()

    def translate(self, text):
        token = self._token_getter.get_token(text)
        params = make_params(self._from, self._to, token, text)
        r = self._session.get('https://{}/translate_a/single'.format(self._domain), params=params)
        if r.status_code != 200:
            raise GGXlatError('Refreshing token, request got {}'.format(r.status_code))
        results = json.loads(r.text)
        if self._dict_mode and results[1] is not None:
            return '\n'.join('{}: {}'.format(pos, ', '.join(explains)) for pos, explains, *_ in results[1])
        else:
            return ''.join(r.strip() for r in (result[0] for result in results[0]) if r is not None)

_global_token_getter = TokenGetter()


def translate(text, from_lang='auto', to_lang='zh-CN'):
    translator = Translator(_global_token_getter, from_lang=from_lang, to_lang=to_lang)
    return translator.translate(text)
