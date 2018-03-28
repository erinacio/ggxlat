import argparse
from typing import NamedTuple
import io
import sys
import os

from . import Translator, TokenGetter
from .vendor.appdirs import user_cache_dir


def make_arg_parser():
    parser = argparse.ArgumentParser(description='Translate text with Google Translator')
    parser.add_argument('--from', '-f',
                        nargs=1, default='auto',
                        help='language code of source language (e.g. "en")')

    parser.add_argument('--to', '-t',
                        nargs=1, default='zh-CN',
                        help='language code of destination language (e.g. "zh-CN")')

    parser.add_argument('--output', '-o',
                        nargs='?',
                        help='destination of translation')

    parser.add_argument('--dict', '-d',
                        action='store_true',
                        help='show dictionary explanation if possible')

    parser.add_argument('--expr', '-e',
                        help='expression to be translated, will override [input]')

    parser.add_argument('input',
                        nargs='?',
                        help='input file, or STDIN if omitted')
    return parser


class Argument(NamedTuple):
    from_lang: str
    to_lang: str
    out_fp: io.IOBase
    text: str
    enable_dict: bool


def parse_arg(parser=None):
    parser = make_arg_parser() if parser is None else parser
    parsed = parser.parse_args()
    out_fp = open(parsed.output) if parsed.output is not None else sys.stdout
    text = parsed.expr
    if text is None:
        in_fp = open(parsed.input) if parsed.input is not None else sys.stdin
        try:
            text = in_fp.read()
            if type(text) is bytes:
                text = text.decode()
        finally:
            in_fp.close()
    return Argument(from_lang = getattr(parsed, 'from'),
                    to_lang = parsed.to,
                    out_fp = out_fp,
                    text = text,
                    enable_dict = parsed.dict)


def prepare_cache():
    cache_dir = user_cache_dir('ggxlat', 'me.erinacio')
    os.makedirs(cache_dir, mode=0o700, exist_ok=True)
    return os.path.join(cache_dir, 'token')


def main():
    cache_file = prepare_cache()
    token_getter = TokenGetter.try_reload(cache_file)
    token_getter.refresh_token()
    token_getter.save_to(cache_file)

    arg = parse_arg()
    try:
        translator = Translator(token_getter, from_lang=arg.from_lang, to_lang=arg.to_lang, dict_mode=arg.enable_dict)
        print(translator.translate(arg.text), file=arg.out_fp)
    finally:
        arg.out_fp.close()

if __name__ == '__main__': main()
