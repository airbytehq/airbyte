import requests

def get_group_list(**kwargs):
    headers = kwargs["authenticator"].get_auth_header()

    ids = []

    r = requests.get(f'https://{kwargs["api_url"]}/api/v4/groups?page=1&per_page=50', headers=headers)
    results = r.json()
    items = map(lambda i: i['full_path'].replace('/', '%2f'), results)
    ids.extend(items)

    while 'X-Next-Page' in r.headers and r.headers['X-Next-Page'] != '':
        next_page = r.headers['X-Next-Page']
        per_page = r.headers['X-Per-Page']
        r = requests.get(f'https://{kwargs["api_url"]}/api/v4/groups?page={next_page}&per_page={per_page}', headers=headers)
        results = r.json()
        items = map(lambda i: i['full_path'].replace('/', '%2f'), results)
        ids.extend(items)

    return ids
