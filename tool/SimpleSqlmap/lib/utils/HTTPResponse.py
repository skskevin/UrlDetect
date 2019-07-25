import mimetools
import StringIO

_MAXLINE = 65536
_UNKNOWN = 'UNKNOWN'
_MAXHEADERS = 100

CONTINUE = 100
NO_CONTENT = 204
NOT_MODIFIED = 304



class LineAndFileWrapper:
    """A limited file-like object for HTTP/0.9 responses."""

    # The status-line parsing code calls readline(), which normally
    # get the HTTP status line.  For a 0.9 response, however, this is
    # actually the first line of the body!  Clients need to get a
    # readable file object that contains that line.

    def __init__(self, line, file):
        self._line = line
        self._file = file
        self._line_consumed = 0
        self._line_offset = 0
        self._line_left = len(line)

    def __getattr__(self, attr):
        return getattr(self._file, attr)

    def _done(self):
        # called when the last byte is read from the line.  After the
        # call, all read methods are delegated to the underlying file
        # object.
        self._line_consumed = 1
        self.read = self._file.read
        self.readline = self._file.readline
        self.readlines = self._file.readlines

    def read(self, amt=None):
        if self._line_consumed:
            return self._file.read(amt)
        assert self._line_left
        if amt is None or amt > self._line_left:
            s = self._line[self._line_offset:]
            self._done()
            if amt is None:
                return s + self._file.read()
            else:
                return s + self._file.read(amt - len(s))
        else:
            assert amt <= self._line_left
            i = self._line_offset
            j = i + amt
            s = self._line[i:j]
            self._line_offset = j
            self._line_left -= amt
            if self._line_left == 0:
                self._done()
            return s

    def readline(self):
        if self._line_consumed:
            return self._file.readline()
        assert self._line_left
        s = self._line[self._line_offset:]
        self._done()
        return s

    def readlines(self, size=None):
        if self._line_consumed:
            return self._file.readlines(size)
        assert self._line_left
        L = [self._line[self._line_offset:]]
        self._done()
        if size is None:
            return L + self._file.readlines()
        else:
            return L + self._file.readlines(size)

class HTTPMessage(mimetools.Message):

    def addheader(self, key, value):
        """Add header for field key handling repeats."""
        prev = self.dict.get(key)
        if prev is None:
            self.dict[key] = value
        else:
            combined = ", ".join((prev, value))
            self.dict[key] = combined

    def addcontinue(self, key, more):
        """Add more field data from a continuation line."""
        prev = self.dict[key]
        self.dict[key] = prev + "\n " + more

    def readheaders(self):
        """Read header lines.

        Read header lines up to the entirely blank line that terminates them.
        The (normally blank) line that ends the headers is skipped, but not
        included in the returned list.  If a non-header line ends the headers,
        (which is an error), an attempt is made to backspace over it; it is
        never included in the returned list.

        The variable self.status is set to the empty string if all went well,
        otherwise it is an error message.  The variable self.headers is a
        completely uninterpreted list of lines contained in the header (so
        printing them will reproduce the header exactly as it appears in the
        file).

        If multiple header fields with the same name occur, they are combined
        according to the rules in RFC 2616 sec 4.2:

        Appending each subsequent field-value to the first, each separated
        by a comma. The order in which header fields with the same field-name
        are received is significant to the interpretation of the combined
        field value.
        """
        # XXX The implementation overrides the readheaders() method of
        # rfc822.Message.  The base class design isn't amenable to
        # customized behavior here so the method here is a copy of the
        # base class code with a few small changes.

        self.dict = {}
        self.unixfrom = ''
        self.headers = hlist = []
        self.status = ''
        headerseen = ""
        firstline = 1
        startofline = unread = tell = None
        if hasattr(self.fp, 'unread'):
            unread = self.fp.unread
        elif self.seekable:
            tell = self.fp.tell
        while True:
            if len(hlist) > _MAXHEADERS:
                raise HTTPException("got more than %d headers" % _MAXHEADERS)
            if tell:
                try:
                    startofline = tell()
                except IOError:
                    startofline = tell = None
                    self.seekable = 0
            line = self.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong("header line")
            if not line:
                self.status = 'EOF in headers'
                break
            # Skip unix From name time lines
            if firstline and line.startswith('From '):
                self.unixfrom = self.unixfrom + line
                continue
            firstline = 0
            if headerseen and line[0] in ' \t':
                # XXX Not sure if continuation lines are handled properly
                # for http and/or for repeating headers
                # It's a continuation line.
                hlist.append(line)
                self.addcontinue(headerseen, line.strip())
                continue
            elif self.iscomment(line):
                # It's a comment.  Ignore it.
                continue
            elif self.islast(line):
                # Note!  No pushback here!  The delimiter line gets eaten.
                break
            headerseen = self.isheader(line)
            if headerseen:
                # It's a legal header line, save it.
                hlist.append(line)
                self.addheader(headerseen, line[len(headerseen) + 1:].strip())
                continue
            else:
                # It's not a header line; throw it back and stop here.
                if not self.dict:
                    self.status = 'No headers'
                else:
                    self.status = 'Non-header line where header expected'
                # Try to undo the read.
                if unread:
                    unread(line)
                elif tell:
                    self.fp.seek(startofline)
                else:
                    self.status = self.status + '; bad seek'
                break

class HTTPResponse:
    def __init__(self, buff):
        self.version = _UNKNOWN # HTTP-Version
        self.status = _UNKNOWN  # Status-Code
        self.reason = _UNKNOWN  # Reason-Phrase
        self.data   = _UNKNOWN  # data

        self.chunked = _UNKNOWN         # is "chunked" being used?
        self.chunk_left = _UNKNOWN      # bytes left to read in current chunk
        self.length = _UNKNOWN          # number of bytes left in response


        s_buf = StringIO.StringIO(buff)     # 将buff赋值给StringIO对象
        #s_buf.buf = buff                   # 将buff指针直接给过去 后面的read（）会出现空指针


        self.fp = s_buf
    def _read_status(self):
        line = self.fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            print "Error"
        if not line:
            print "Error"
        try:
            [version, status, reason] = line.split(None, 2)
        except ValueError:
            try:
                [version, status] = line.split(None, 1)
                reason = ""
            except ValueError:
                version = ""
        if not version.startswith('HTTP/'):
            self.fp = LineAndFileWrapper(line, self.fp)
            return "HTTP/0.9", 200, ""
        try:
            status = int(status)
            if status < 100 or status > 999:
                print "Error"
        except ValueError:
            print "Error"
        return version, status, reason
    def _check_close(self):
        conn = self.msg.getheader('connection')
        if self.version == 11:
            # An HTTP/1.1 proxy is assumed to stay open unless
            # explicitly closed.
            conn = self.msg.getheader('connection')
            if conn and "close" in conn.lower():
                return True
            return False

        # Some HTTP/1.0 implementations have support for persistent
        # connections, using rules different than HTTP/1.1.

        # For older HTTP, Keep-Alive indicates persistent connection.
        if self.msg.getheader('keep-alive'):
            return False

        # At least Akamai returns a "Connection: Keep-Alive" header,
        # which was supposed to be sent by the client.
        if conn and "keep-alive" in conn.lower():
            return False

        # Proxy-Connection is a netscape hack.
        pconn = self.msg.getheader('proxy-connection')
        if pconn and "keep-alive" in pconn.lower():
            return False

        # otherwise, assume it will close
        return True


    def begin(self):
        while True:
            version, status, reason = self._read_status()
            if status != CONTINUE:
                break
            while True:
                skip = self.fp.readline(_MAXLINE + 1)
                if len(skip) > _MAXLINE:
                    print "header line"
                skip = skip.strip()
                if not skip:
                    break
        self.status = status
        self.reason = reason.strip()
        if version == 'HTTP/1.0':
            self.version = 10
        elif version.startswith('HTTP/1.'):
            self.version = 11   # use HTTP/1.1 code for HTTP/1.x where x>=1
        elif version == 'HTTP/0.9':
            self.version = 9
        else:
            print "Error"



        if self.version == 9:
            self.length = None
            self.chunked = 0
            self.will_close = 1
            self.msg = HTTPMessage(StringIO())
            return


        self.msg = HTTPMessage(self.fp, 0)
        self.msg.fp = None

        self.data = self.fp.read()

        tr_enc = self.msg.getheader('transfer-encoding')
        if tr_enc and tr_enc.lower() == "chunked":
            self.chunked = 1
            self.chunk_left = None
        else:
            self.chunked = 0
        self.will_close = self._check_close()
        length = self.msg.getheader('content-length')
        if length and not self.chunked:
            try:
                self.length = int(length)
            except ValueError:
                self.length = None
            else:
                if self.length < 0:  # ignore nonsensical negative lengths
                    self.length = None
        else:
            self.length = None

        if (status == NO_CONTENT or status == NOT_MODIFIED or 100 <= status < 200):
            self.length = 0

        if not self.will_close and \
           not self.chunked and \
           self.length is None:
            self.will_close = 1

    def getheader(self, name, default=None):
        if self.msg is None:
            pass
        return self.msg.getheader(name, default)

    def getheaders(self):
        """Return list of (header, value) tuples."""
        if self.msg is None:
            pass
        return self.msg.dict
        #return self.msg.items()

    def getdata(self):
        """Return list of (header, value) tuples."""
        if self.msg is None:
            pass
        return self.data

    def getstatus(self):
        """Return list of (header, value) tuples."""
        if self.msg is None:
            pass
        return self.status
