import math

# Translated from https://github.com/matheuss/google-translate-token/blob/master/index.js


def urshift(x, a):
    '''`x >>> a` as in Javascript'''
    return (x & 0xffffffff) >> (a & 0x1f)


def lshift(x, a):
    '''`x << a` as in Javascript'''
    x = (x << (a & 0x1F)) & 0xffffffff
    return x if x <= 0x7fffffff else x - 0x100000000


def to_int(x, default=None):
    try:
        return int(x)
    except ValueError:
        return default


def str_to_utf16(s):
    b = s.encode('utf-16le')
    return [b[i] + (b[i + 1] << 8) for i in range(0, len(b), 2)]


def xr(a, b):
    for c in range(0, len(b) - 2, 3):
        d = b[c + 2]
        d1 = ord(d) - 87 if 'a' <= d else int(d)
        d2 = urshift(a, d1) if '+' == b[c + 1] else lshift(a, d1)
        a = (a + d2) & 0xffffffff if '+' == b[c] else a ^ d2
    return a


def sM(a, tk):
    a = str_to_utf16(a)
    a.append(0)
    b = tk or ''
    c1 = '&tk='
    d = b.split('.')
    b = to_int(d[0], default=0)

    e = []
    g = 0
    len_a = len(a) - 1
    while g < len_a:
        l = a[g]
        if 128 > l:
            e.append(l)
        else:
            if 2048 > l:
                e.append((l >> 6) | 192)
            else:
                if 55296 == (l & 64512) and g + 1 < len(a) and 56320 == (a[g + 1] & 64512):
                    g += 1
                    l = 65536 + ((l & 1023) << 10) + (a[g] & 1023)
                    e.append((l >> 18) | 240)
                    e.append(((l >> 12) & 63) | 128)
                else:
                    e.append((l >> 12) | 224)
                e.append(((l >> 6) & 63) | 128)
            e.append((l & 63) | 128)
        g += 1
    a = b
    for f in e:
        a += f
        a = xr(a, '+-a^+6')
    a = xr(a, '+-3^+b+-f')
    a ^= to_int(d[1], 0)
    if 0 > a:
        a = (a & 2147483647) + 2147483648
    a %= 1000000
    return '{}.{}'.format(a, (a ^ b))
