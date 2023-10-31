from xmlrpc import client


class CookiesTransport(client.Transport):
    """A Transport subclass that retains cookies over its lifetime."""

    def __init__(self):
        super().__init__()
        self._cookies = []

    def send_headers(self, connection, headers):
        if self._cookies:
            connection.putheader("Cookie", "; ".join(self._cookies))
        super().send_headers(connection, headers)

    def parse_response(self, response):
        cookies = response.msg.get_all("Set-Cookie")
        if cookies:
            for header in response.msg.get_all("Set-Cookie"):
                cookie = header.split(";", 1)[0]
                self._cookies.append(cookie)
        return super().parse_response(response)


SapeClient = client.ServerProxy("https://api.sape.ru/xmlrpc/", transport=CookiesTransport())
