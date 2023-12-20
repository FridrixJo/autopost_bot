from urllib import request
import re

link = 'https://t.me/denis_mscw'


def check(url):
    reg = r'http'
    x = re.match(pattern=reg, string=url)
    if x is not None:
        return True
    else:
        return False


print(check(link))
