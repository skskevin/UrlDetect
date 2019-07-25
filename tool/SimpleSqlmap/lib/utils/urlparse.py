import re
import os



__all__ = ["urlparse", "urlunparse", "urljoin", "urldefrag",
           "urlsplit", "urlunsplit", "parse_qs", "parse_qsl"]


uses_relative = ['ftp', 'http', 'gopher', 'nntp', 'imap',
                 'wais', 'file', 'https', 'shttp', 'mms',
                 'prospero', 'rtsp', 'rtspu', '', 'sftp',
                 'svn', 'svn+ssh']

uses_netloc = ['ftp', 'http', 'gopher', 'nntp', 'telnet',
               'imap', 'wais', 'file', 'mms', 'https', 'shttp',
               'snews', 'prospero', 'rtsp', 'rtspu', 'rsync', '',
               'svn', 'svn+ssh', 'sftp','nfs','git', 'git+ssh']

uses_params = ['ftp', 'hdl', 'prospero', 'http', 'imap',
               'https', 'shttp', 'rtsp', 'rtspu', 'sip', 'sips',
               'mms', '', 'sftp', 'tel']

non_hierarchical = ['gopher', 'hdl', 'mailto', 'news',
                    'telnet', 'wais', 'imap', 'snews', 'sip', 'sips']

uses_query = ['http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips', '']

uses_fragment = ['ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero', '']

scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

MAX_CACHE_SIZE = 20
_parse_cache = {}

def clear_cache():
    """Clear the parse cache."""
    _parse_cache.clear()

class ResultMixin(object):
    """Shared methods for the parsed result objects."""

    @property
    def username(self):
        netloc = self.netloc
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                userinfo = userinfo.split(":", 1)[0]
            return userinfo
        return None

    @property
    def password(self):
        netloc = self.netloc
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                return userinfo.split(":", 1)[1]
        return None

    @property
    def hostname(self):
        netloc = self.netloc.split('@')[-1]
        if '[' in netloc and ']' in netloc:
            return netloc.split(']')[0][1:].lower()
        elif ':' in netloc:
            return netloc.split(':')[0].lower()
        elif netloc == '':
            return None
        else:
            return netloc.lower()

    @property
    def port(self):
        netloc = self.netloc.split('@')[-1].split(']')[-1]
        if ':' in netloc:
            port = netloc.split(':')[1]
            if port:
                port = int(port, 10)
                # verify legal port
                if (0 <= port <= 65535):
                    return port
        return None

from collections import namedtuple

class SplitResult(namedtuple('SplitResult', 'scheme netloc path query fragment path_list'), ResultMixin):

    __slots__ = ()

    def geturl(self):
        return urlunsplit(self)


class ParseResult(namedtuple('ParseResult', 'scheme netloc path params query fragment path_list url_file url_ext'), ResultMixin):

    __slots__ = ()

    def geturl(self):
        return urlunparse(self)


def urlparse(url, scheme='', allow_fragments=True):
    tuple = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment, path_list = tuple
    if scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''

    (file, ext) = os.path.splitext(url)
    url_file = scheme + '://' + netloc + file
    url_ext = ext
    return ParseResult(scheme, netloc, url, params, query, fragment, path_list, url_file, url_ext)

def _splitparams(url):
    if '/' in url:
        i = url.find(';', url.rfind('/'))
        if i < 0:
            return url, ''
    else:
        i = url.find(';')
    return url[:i], url[i + 1:]

def _splitnetloc(url, start=0):
    delim = len(url)   # position of end of domain part of url, default is end
    for c in '/?#':    # look for delimiters; the order is NOT important
        wdelim = url.find(c, start)        # find first of this delim
        if wdelim >= 0:                    # if found
            delim = min(delim, wdelim)     # use earliest delim position
    return url[start:delim], url[delim:]   # return (domain, rest)


def urlsplit(url, scheme='', allow_fragments=True):
    """Parse a URL into 5 components:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    Return a 5-tuple: (scheme, netloc, path, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    basics = ''
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, None)
    if cached:
        return cached
    if len(_parse_cache) >= MAX_CACHE_SIZE: # avoid runaway growth
        clear_cache()
    netloc = query = fragment = basics = ''
    path_list = []
    i = url.find(':')
    if i > 0:
        if url[:i] == 'http' or url[:i] == 'https': # optimize the common case
            scheme = url[:i].lower()
            basics = scheme + ':'
            url = url[i + 1:]
            if url[:2] == '//':
                basics += "//"
                netloc, url = _splitnetloc(url, 2)

                basics += netloc
                token_url = url
                if '?' in url:
                    token_url = url.split('?', 1)[0]
                if '#' in url:
                    token_url = url.split('#', 1)[0]

                j = 0
                while (j >= 0):
                    j = token_url.find('/')
                    url_value = token_url[:j]
                    token_url = token_url[j + 1:]
                    j = token_url.find('/')
                    basics = basics + '/' + url_value
                    basics = basics.strip('/')
                    path_list.append(basics)

                if (('[' in netloc and ']' not in netloc) or (']' in netloc and '[' not in netloc)):
                    raise ValueError("Invalid IPv6 URL")
            if allow_fragments and '#' in url:
                url, fragment = url.split('#', 1)
            if '?' in url:
                url, query = url.split('?', 1)
            v = SplitResult(scheme, netloc, url, query, fragment, path_list)
            _parse_cache[key] = v
            return v
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            # make sure "url" is not actually a port number (in which case
            # "scheme" is really part of the path)
            rest = url[i + 1:]
            if not rest or any(c not in '0123456789' for c in rest):
                # not a port number
                scheme, url = url[:i].lower(), rest

    if url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        if (('[' in netloc and ']' not in netloc) or (']' in netloc and '[' not in netloc)):
            raise ValueError("Invalid IPv6 URL")
    if allow_fragments and '#' in url:
        url, fragment = url.split('#', 1)
    if '?' in url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment, path_list)
    _parse_cache[key] = v
    return v