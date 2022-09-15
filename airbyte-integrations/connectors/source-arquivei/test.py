import requests
import base64

# url_base = "https://api.arquivei.com.br/v1/"
url_base = "https://api.arquivei.com.br/v1/nfe/received"
api_key = "f4a7cbd0976b7ccc1d11ec0768e3b343f7f42b1e"
api_id = "d25100f602c9a5ef5e01bf4a9202ddeffcfe50d8"

r = requests.get(url_base, headers={
    "X-API-ID":api_id,
    "X-API-KEY":api_key,
    "Content-Type":"application/json"
})

print(r.status_code)
print('\n\n',r.headers)
# print('\n\n',r.content)  # bytes
print('\n\n',base64.b64decode(r.text))