# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""At its heart, Python can be viewed as an extension of the C
programming language. Springing from the most popular systems
programming language has made Python itself a great language for
systems programming. One key to success in this domain is Python's
very serviceable :mod:`socket` module and its :class:`socket.socket`
type.

The ``socketutils`` module provides natural next steps to the ``socket``
builtin: straightforward, tested building blocks for higher-level
protocols.

The :class:`BufferedSocket` wraps an ordinary socket, providing a
layer of intuitive buffering for both sending and receiving. This
facilitates parsing messages from streams, i.e., all sockets with type
``SOCK_STREAM``. The BufferedSocket enables receiving until the next
relevant token, up to a certain size, or until the connection is
closed. For all of these, it provides consistent APIs to size
limiting, as well as timeouts that are compatible with multiple
concurrency paradigms. Use it to parse the next one-off text or binary
socket protocol you encounter.

This module also provides the :class:`NetstringSocket`, a pure-Python
implementation of `the Netstring protocol`_, built on top of the
:class:`BufferedSocket`, serving as a ready-made, production-grade example.

Special thanks to `Kurt Rose`_ for his original authorship and all his
contributions on this module. Also thanks to `Daniel J. Bernstein`_, the
original author of `Netstring`_.

.. _the Netstring protocol: https://en.wikipedia.org/wiki/Netstring
.. _Kurt Rose: https://github.com/doublereedkurt
.. _Daniel J. Bernstein: https://cr.yp.to/
.. _Netstring: https://cr.yp.to/proto/netstrings.txt

"""

import time
import socket

try:
    from threading import RLock
except Exception:
    class RLock:
        'Dummy reentrant lock for builds without threads'
        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass


try:
    from .typeutils import make_sentinel
    _UNSET = make_sentinel(var_name='_UNSET')
except ImportError:
    _UNSET = object()


DEFAULT_TIMEOUT = 10  # 10 seconds
DEFAULT_MAXSIZE = 32 * 1024  # 32kb
_RECV_LARGE_MAXSIZE = 1024 ** 5  # 1PB


class BufferedSocket:
    """Mainly provides recv_until and recv_size. recv, send, sendall, and
    peek all function as similarly as possible to the built-in socket
    API.

    This type has been tested against both the built-in socket type as
    well as those from gevent and eventlet. It also features support
    for sockets with timeouts set to 0 (aka nonblocking), provided the
    caller is prepared to handle the EWOULDBLOCK exceptions.

    Args:
        sock (socket): The connected socket to be wrapped.
        timeout (float): The default timeout for sends and recvs, in
            seconds. Set to ``None`` for no timeout, and 0 for
            nonblocking. Defaults to *sock*'s own timeout if already set,
            and 10 seconds otherwise.
        maxsize (int): The default maximum number of bytes to be received
            into the buffer before it is considered full and raises an
            exception. Defaults to 32 kilobytes.
        recvsize (int): The number of bytes to recv for every
            lower-level :meth:`socket.recv` call. Defaults to *maxsize*.

    *timeout* and *maxsize* can both be overridden on individual socket
    operations.

    All ``recv`` methods return bytestrings (:class:`bytes`) and can
    raise :exc:`socket.error`. :exc:`Timeout`,
    :exc:`ConnectionClosed`, and :exc:`MessageTooLong` all inherit
    from :exc:`socket.error` and exist to provide better error
    messages. Received bytes are always buffered, even if an exception
    is raised. Use :meth:`BufferedSocket.getrecvbuffer` to retrieve
    partial recvs.

    BufferedSocket does not replace the built-in socket by any
    means. While the overlapping parts of the API are kept parallel to
    the built-in :class:`socket.socket`, BufferedSocket does not
    inherit from socket, and most socket functionality is only
    available on the underlying socket. :meth:`socket.getpeername`,
    :meth:`socket.getsockname`, :meth:`socket.fileno`, and others are
    only available on the underlying socket that is wrapped. Use the
    ``BufferedSocket.sock`` attribute to access it. See the examples
    for more information on how to use BufferedSockets with built-in
    sockets.

    The BufferedSocket is threadsafe, but consider the semantics of
    your protocol before accessing a single socket from multiple
    threads. Similarly, once the BufferedSocket is constructed, avoid
    using the underlying socket directly. Only use it for operations
    unrelated to messages, e.g., :meth:`socket.getpeername`.

    """
    def __init__(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()

    def settimeout(self, timeout):
        "Set the default *timeout* for future operations, in seconds."
        self.timeout = timeout

    def gettimeout(self):
        return self.timeout

    def setblocking(self, blocking):
        self.timeout = None if blocking else 0.0

    def setmaxsize(self, maxsize):
        """Set the default maximum buffer size *maxsize* for future
        operations, in bytes. Does not truncate the current buffer.
        """
        self.maxsize = maxsize

    def getrecvbuffer(self):
        "Returns the receive buffer bytestring (rbuf)."
        with self._recv_lock:
            return self.rbuf

    def getsendbuffer(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(self.sbuf)

    def recv(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def peek(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def recv_close(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def recv_until(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def recv_size(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def send(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def sendall(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, timeout)

    def flush(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'')
        return

    def buffer(self, data):
        "Buffer *data* bytes for the next send operation."
        with self._send_lock:
            self.sbuf.append(data)
        return

    # # #
    # # # Passing through some socket basics
    # # #

    def getsockname(self):
        """Convenience function to return the wrapped socket's own address.
        See :meth:`socket.getsockname` for more details.
        """
        return self.sock.getsockname()

    def getpeername(self):
        """Convenience function to return the remote address to which the
        wrapped socket is connected.  See :meth:`socket.getpeername`
        for more details.
        """
        return self.sock.getpeername()

    def getsockopt(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = (level, optname)
        if buflen is not None:
            args += (buflen,)
        return self.sock.getsockopt(*args)

    def setsockopt(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, optname, value)

    @property
    def type(self):
        """A passthrough to the wrapped socket's type. Valid usages should
        only ever see :data:`socket.SOCK_STREAM`.
        """
        return self.sock.type

    @property
    def family(self):
        """A passthrough to the wrapped socket's family. BufferedSocket
        supports all widely-used families, so this read-only attribute
        can be one of :data:`socket.AF_INET` for IP,
        :data:`socket.AF_INET6` for IPv6, and :data:`socket.AF_UNIX`
        for UDS.
        """
        return self.sock.family

    @property
    def proto(self):
        """A passthrough to the wrapped socket's protocol. The ``proto``
        attribute is very rarely used, so it's always 0, meaning "the
        default" protocol. Pretty much all the practical information
        is in :attr:`~BufferedSocket.type` and
        :attr:`~BufferedSocket.family`, so you can go back to never
        thinking about this.
        """
        return self.sock.proto

    # # #
    # # # Now for some more advanced interpretations of the builtin socket
    # # #

    def fileno(self):
        """Returns the file descriptor of the wrapped socket. -1 if it has
        been closed on this end.

        Note that this makes the BufferedSocket selectable, i.e.,
        usable for operating system event loops without any external
        libraries. Keep in mind that the operating system cannot know
        about data in BufferedSocket's internal buffer. Exercise
        discipline with calling ``recv*`` functions.
        """
        return self.sock.fileno()

    def close(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def shutdown(self, how):
        """Convenience method which passes through to the wrapped socket's
        :meth:`~socket.shutdown`. Semantics vary by platform, so no
        special internal handling is done with the buffers. This
        method exists to facilitate the most common usage, wherein a
        full ``shutdown`` is followed by a
        :meth:`~BufferedSocket.close`. Developers requiring more
        support, please open `an issue`_.

        .. _an issue: https://github.com/mahmoud/boltons/issues
        """
        with self._recv_lock:
            with self._send_lock:
                self.sock.shutdown(how)
        return

    # end BufferedSocket


class Error(socket.error):
    """A subclass of :exc:`socket.error` from which all other
    ``socketutils`` exceptions inherit.

    When using :class:`BufferedSocket` and other ``socketutils``
    types, generally you want to catch one of the specific exception
    types below, or :exc:`socket.error`.
    """
    pass


class ConnectionClosed(Error):
    """Raised when receiving and the connection is unexpectedly closed
    from the sending end. Raised from :class:`BufferedSocket`'s
    :meth:`~BufferedSocket.peek`, :meth:`~BufferedSocket.recv_until`,
    and :meth:`~BufferedSocket.recv_size`, and never from its
    :meth:`~BufferedSocket.recv` or
    :meth:`~BufferedSocket.recv_close`.
    """
    pass


class MessageTooLong(Error):
    """Raised from :meth:`BufferedSocket.recv_until` and
    :meth:`BufferedSocket.recv_closed` when more than *maxsize* bytes are
    read without encountering the delimiter or a closed connection,
    respectively.
    """
    def __init__(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)


class Timeout(socket.timeout, Error):
    """Inheriting from :exc:`socket.timeout`, Timeout is used to indicate
    when a socket operation did not complete within the time
    specified. Raised from any of :class:`BufferedSocket`'s ``recv``
    methods.
    """
    def __init__(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)


class NetstringSocket:
    """
    Reads and writes using the netstring protocol.

    More info: https://en.wikipedia.org/wiki/Netstring
    Even more info: http://cr.yp.to/proto/netstrings.txt
    """
    def __init__(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10

    def fileno(self):
        return self.bsock.fileno()

    def settimeout(self, timeout):
        self.timeout = timeout

    def setmaxsize(self, maxsize):
        self.maxsize = maxsize
        self._msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

    def _calc_msgsize_maxsize(self, maxsize):
        return len(str(maxsize)) + 1  # len(str()) == log10

    def read_ns(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def write_ns(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)


class NetstringProtocolError(Error):
    "Base class for all of socketutils' Netstring exception types."
    pass


class NetstringInvalidSize(NetstringProtocolError):
    """NetstringInvalidSize is raised when the ``:``-delimited size prefix
    of the message does not contain a valid integer.

    Message showing valid size::

      5:hello,

    Here the ``5`` is the size. Anything in this prefix position that
    is not parsable as a Python integer (i.e., :class:`int`) will raise
    this exception.
    """
    def __init__(self, msg):
        super().__init__(msg)


class NetstringMessageTooLong(NetstringProtocolError):
    """NetstringMessageTooLong is raised when the size prefix contains a
    valid integer, but that integer is larger than the
    :class:`NetstringSocket`'s configured *maxsize*.

    When this exception is raised, it's recommended to simply close
    the connection instead of trying to recover.
    """
    def __init__(self, size, maxsize):
        msg = ('netstring message length exceeds configured maxsize: %s > %s'
               % (size, maxsize))
        super().__init__(msg)


"""
attrs worth adding/passing through:


properties: type, proto

For its main functionality, BufferedSocket can wrap any object that
has the following methods:

  - gettimeout()
  - settimeout()
  - recv(size)
  - send(data)

The following methods are passed through:

...

"""

# TODO: buffered socket check socket.type == SOCK_STREAM?
# TODO: make recv_until support taking a regex
# TODO: including the delimiter in the recv_until return is not
#       necessary, as ConnectionClosed differentiates empty messages
#       from socket closes.
