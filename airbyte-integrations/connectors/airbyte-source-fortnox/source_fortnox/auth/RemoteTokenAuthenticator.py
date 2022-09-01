import requests
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase, HTTPBasicAuth
from requests.packages.urllib3.util.retry import Retry


class RemoteTokenAuthenticator(AuthBase):
    def __init__(
            self,
            url: str,
            service_id: str,
            project_code: str,
            username: str,
            password: str,
            package: str = 'default',
            **kwargs
    ):
        self.url = url
        self.service_id = service_id
        self.project_code = project_code
        self.username = username
        self.password = password
        self.package = package
        self.session = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.5,
            status_forcelist=[429],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)

    def __call__(self, request):
        request.headers.update({"Authorization": f"Bearer {self.get_access_token()}"})
        return request

    def get_access_token(self):
        try:
            response = self.session.post(url=self.url,
                                         json=dict(
                                             service=self.service_id,
                                             project_code=self.project_code,
                                             package=self.package
                                         ),
                                         auth=HTTPBasicAuth(self.username, self.password))
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Error while getting access token: {e}") from e
