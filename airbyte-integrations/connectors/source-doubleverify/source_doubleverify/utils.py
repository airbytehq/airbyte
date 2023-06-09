import re

class Utils(object):
    def get_request_header(config, accept:str = "*/*", content_type:str ="application/json", accept_encoding:str = "gzip, deflate, br"):
        access_token = config.get("access_token")
        return {
            "Authorization": "Bearer "+"{}".format(access_token),
            "Accept" : "{}".format(accept),
            "Content-Type": "{}".format(content_type),
            "Accept-Encoding" : "{}".format(accept_encoding)
        }

    def sanitize(s: str):
        s = s.replace("variables/", "")
        s = s.replace("metrics/", "")
        s = re.sub('[\s/-]+', '_', s.strip())
        # Remove punctuation, which is anything that is not either a word or a whitespace character
        s = re.sub('[^\w\s]+', '', s)
        return s.lower()