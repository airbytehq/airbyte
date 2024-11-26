import warnings

import deprecated
import urllib3

import github
from github import Consts
from github.Auth import AppAuth
from github.GithubApp import GithubApp
from github.GithubException import GithubException
from github.Installation import Installation
from github.InstallationAuthorization import InstallationAuthorization
from github.PaginatedList import PaginatedList
from github.Requester import Requester


class GithubIntegration:
    """
    Main class to obtain tokens for a GitHub integration.
    """

    # keep non-deprecated arguments in-sync with Requester
    # v2: remove integration_id, private_key, jwt_expiry, jwt_issued_at and jwt_algorithm
    # v2: move auth to the front of arguments
    # v2: move * before first argument so all arguments must be named,
    #     allows to reorder / add new arguments / remove deprecated arguments without breaking user code
    #     added here to force named parameters because new parameters have been added
    def __init__(
        self,
        integration_id=None,
        private_key=None,
        base_url=Consts.DEFAULT_BASE_URL,
        *,
        timeout=Consts.DEFAULT_TIMEOUT,
        user_agent=Consts.DEFAULT_USER_AGENT,
        per_page=Consts.DEFAULT_PER_PAGE,
        verify=True,
        retry=None,
        pool_size=None,
        jwt_expiry=Consts.DEFAULT_JWT_EXPIRY,
        jwt_issued_at=Consts.DEFAULT_JWT_ISSUED_AT,
        jwt_algorithm=Consts.DEFAULT_JWT_ALGORITHM,
        auth=None,
    ):
        """
        :param integration_id: int deprecated, use auth=github.Auth.AppAuth(...) instead
        :param private_key: string deprecated, use auth=github.Auth.AppAuth(...) instead
        :param base_url: string
        :param timeout: integer
        :param user_agent: string
        :param per_page: int
        :param verify: boolean or string
        :param retry: int or urllib3.util.retry.Retry object
        :param pool_size: int
        :param jwt_expiry: int deprecated, use auth=github.Auth.AppAuth(...) instead
        :param jwt_issued_at: int deprecated, use auth=github.Auth.AppAuth(...) instead
        :param jwt_algorithm: string deprecated, use auth=github.Auth.AppAuth(...) instead
        :param auth: authentication method
        """
        if integration_id is not None:
            assert isinstance(integration_id, (int, str)), integration_id
        if private_key is not None:
            assert isinstance(
                private_key, str
            ), "supplied private key should be a string"
        assert isinstance(base_url, str), base_url
        assert isinstance(timeout, int), timeout
        assert user_agent is None or isinstance(user_agent, str), user_agent
        assert isinstance(per_page, int), per_page
        assert isinstance(verify, (bool, str)), verify
        assert (
            retry is None
            or isinstance(retry, int)
            or isinstance(retry, urllib3.util.Retry)
        ), retry
        assert pool_size is None or isinstance(pool_size, int), pool_size
        assert isinstance(jwt_expiry, int), jwt_expiry
        assert Consts.MIN_JWT_EXPIRY <= jwt_expiry <= Consts.MAX_JWT_EXPIRY, jwt_expiry
        assert isinstance(jwt_issued_at, int)

        self.base_url = base_url

        if (
            integration_id is not None
            or private_key is not None
            or jwt_expiry != Consts.DEFAULT_JWT_EXPIRY
            or jwt_issued_at != Consts.DEFAULT_JWT_ISSUED_AT
            or jwt_algorithm != Consts.DEFAULT_JWT_ALGORITHM
        ):
            warnings.warn(
                "Arguments integration_id, private_key, jwt_expiry, jwt_issued_at and jwt_algorithm are deprecated, "
                "please use auth=github.Auth.AppAuth(...) instead",
                category=DeprecationWarning,
            )
            auth = AppAuth(
                integration_id,
                private_key,
                jwt_expiry=jwt_expiry,
                jwt_issued_at=jwt_issued_at,
                jwt_algorithm=jwt_algorithm,
            )

        assert isinstance(
            auth, AppAuth
        ), f"GithubIntegration requires github.Auth.AppAuth authentication, not {type(auth)}"

        self.auth = auth

        self.__requester = Requester(
            auth=auth,
            base_url=self.base_url,
            timeout=timeout,
            user_agent=user_agent,
            per_page=per_page,
            verify=verify,
            retry=retry,
            pool_size=pool_size,
        )

    def get_github_for_installation(self, installation_id):
        # The installation has to authenticate as an installation, not an app
        auth = self.auth.get_installation_auth(
            installation_id, requester=self.__requester
        )
        return github.Github(**self.__requester.withAuth(auth).kwargs)

    def _get_headers(self):
        """
        Get headers for the requests.

        :return: dict
        """
        return {
            "Accept": Consts.mediaTypeIntegrationPreview,
        }

    def _get_installed_app(self, url):
        """
        Get installation for the given URL.

        :param url: str
        :rtype: :class:`github.Installation.Installation`
        """
        headers, response = self.__requester.requestJsonAndCheck(
            "GET", url, headers=self._get_headers()
        )

        return Installation(
            requester=self.__requester,
            headers=headers,
            attributes=response,
            completed=True,
        )

    @deprecated.deprecated(
        "Use github.Github(auth=github.Auth.AppAuth), github.Auth.AppAuth.token or github.Auth.AppAuth.create_jwt(expiration) instead"
    )
    def create_jwt(self, expiration=None):
        """
        Create a signed JWT
        https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-a-github-app

        :return string:
        """
        return self.auth.create_jwt(expiration)

    def get_access_token(self, installation_id, permissions=None):
        """
        :calls: `POST /app/installations/{installation_id}/access_tokens <https://docs.github.com/en/rest/apps/apps#create-an-installation-access-token-for-an-app>`
        :param installation_id: int
        :param permissions: dict
        :return: :class:`github.InstallationAuthorization.InstallationAuthorization`
        """
        if permissions is None:
            permissions = {}

        if not isinstance(permissions, dict):
            raise GithubException(
                status=400, data={"message": "Invalid permissions"}, headers=None
            )

        body = {"permissions": permissions}
        headers, response = self.__requester.requestJsonAndCheck(
            "POST",
            f"/app/installations/{installation_id}/access_tokens",
            headers=self._get_headers(),
            input=body,
        )

        return InstallationAuthorization(
            requester=self.__requester,
            headers=headers,
            attributes=response,
            completed=True,
        )

    @deprecated.deprecated("Use get_repo_installation")
    def get_installation(self, owner, repo):
        """
        Deprecated by get_repo_installation

        :calls: `GET /repos/{owner}/{repo}/installation <https://docs.github.com/en/rest/reference/apps#get-a-repository-installation-for-the-authenticated-app>`
        :param owner: str
        :param repo: str
        :rtype: :class:`github.Installation.Installation`
        """
        return self._get_installed_app(url=f"/repos/{owner}/{repo}/installation")

    def get_installations(self):
        """
        :calls: GET /app/installations <https://docs.github.com/en/rest/reference/apps#list-installations-for-the-authenticated-app>
        :rtype: :class:`github.PaginatedList.PaginatedList[github.Installation.Installation]`
        """
        return PaginatedList(
            contentClass=Installation,
            requester=self.__requester,
            firstUrl="/app/installations",
            firstParams=None,
            headers=self._get_headers(),
            list_item="installations",
        )

    def get_org_installation(self, org):
        """
        :calls: `GET /orgs/{org}/installation <https://docs.github.com/en/rest/apps/apps#get-an-organization-installation-for-the-authenticated-app>`
        :param org: str
        :rtype: :class:`github.Installation.Installation`
        """
        return self._get_installed_app(url=f"/orgs/{org}/installation")

    def get_repo_installation(self, owner, repo):
        """
        :calls: `GET /repos/{owner}/{repo}/installation <https://docs.github.com/en/rest/reference/apps#get-a-repository-installation-for-the-authenticated-app>`
        :param owner: str
        :param repo: str
        :rtype: :class:`github.Installation.Installation`
        """
        return self._get_installed_app(url=f"/repos/{owner}/{repo}/installation")

    def get_user_installation(self, username):
        """
        :calls: `GET /users/{username}/installation <https://docs.github.com/en/rest/apps/apps#get-a-user-installation-for-the-authenticated-app>`
        :param username: str
        :rtype: :class:`github.Installation.Installation`
        """
        return self._get_installed_app(url=f"/users/{username}/installation")

    def get_app_installation(self, installation_id):
        """
        :calls: `GET /app/installations/{installation_id} <https://docs.github.com/en/rest/apps/apps#get-an-installation-for-the-authenticated-app>`
        :param installation_id: int
        :rtype: :class:`github.Installation.Installation`
        """
        return self._get_installed_app(url=f"/app/installations/{installation_id}")

    def get_app(self):
        """
        :calls: `GET /app <https://docs.github.com/en/rest/reference/apps#get-the-authenticated-app>`_
        :rtype: :class:`github.GithubApp.GithubApp`
        """

        headers, data = self.__requester.requestJsonAndCheck(
            "GET", "/app", headers=self._get_headers()
        )
        return GithubApp(
            requester=self.__requester, headers=headers, attributes=data, completed=True
        )
