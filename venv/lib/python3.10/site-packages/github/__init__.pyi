from github import Auth as Auth
from github.AppAuthentication import AppAuthentication as AppAuthentication
from github.GithubIntegration import GithubIntegration as GithubIntegration
from github.MainClass import Github as Github

from .GithubException import BadAttributeException as BadAttributeException
from .GithubException import BadCredentialsException as BadCredentialsException
from .GithubException import BadUserAgentException as BadUserAgentException
from .GithubException import GithubException as GithubException
from .GithubException import IncompletableObject as IncompletableObject
from .GithubException import RateLimitExceededException as RateLimitExceededException
from .GithubException import TwoFactorException as TwoFactorException
from .GithubException import UnknownObjectException as UnknownObjectException
from .InputFileContent import InputFileContent as InputFileContent
from .InputGitAuthor import InputGitAuthor as InputGitAuthor
from .InputGitTreeElement import InputGitTreeElement as InputGitTreeElement

def enable_console_debug_logging() -> None: ...
