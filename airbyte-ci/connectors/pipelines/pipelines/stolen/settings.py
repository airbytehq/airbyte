import os
import platform
from typing import Any, Callable, List, Optional

import platformdirs
from dagger import Client, Container
from pydantic import BaseSettings, Field, SecretBytes, SecretStr
from pygit2 import Commit, Repository  #type: ignore

from .singleton import Singleton


def get_git_revision() -> str:
    repo = Repository(".") 
    commit_hash:str = os.environ.get("LAST_COMMIT_SHA", repo.revparse_single("HEAD").hex )
    return commit_hash

def get_current_branch() -> str:    
    repo = Repository(".")                                                                                                                                                                                                                                                                                                                           
    return str(repo.head.shorthand)                                                                                                                                                                   
                                                                                                                                                                                                
def get_latest_commit_message() -> str:   
    repo = Repository(".")                                                                                                                                                                                                                                                                                                                      
    commit: Commit = repo[os.environ.get("LAST_COMMIT_SHA", repo.head.target)]                                                                                                                                                             
    return str(commit.message)                                                                                                                                                                   
                                                                                                                                                                                                
def get_latest_commit_author() -> str:  
    repo: Repository = Repository(".")                                                                                                                                                                                                                                                                                                                       
    commit: Commit = repo[os.environ.get("LAST_COMMIT_SHA", repo.head.target)]                                                                                                                                                              
    return str(commit.author.name)                                                                                                                                                               
                                                                                                                                                                                                
def get_latest_commit_time() -> str:    
    repo = Repository(".")                                                                                                                                                                                                                                                                                                                      
    commit: Commit = repo[os.environ.get("LAST_COMMIT_SHA", repo.head.target)]                                                                                                                                                              
    return str(commit.commit_time)       

def get_repo_root_path() -> str:
    repo = Repository(".")
    return str(os.path.dirname(os.path.dirname(repo.path)))

def get_repo_fullname() -> str:                                                                                              
    repo = Repository(".")
    repo_url:str = repo.remotes["origin"].url
    
    # Handle HTTPS URLs
    if "https://" in repo_url:
        parts = repo_url.split("/")
        owner = parts[-2]
        repo_name = parts[-1].replace(".git", "")
    
    # Handle SSH URLs
    else:
        repo_url = repo_url.replace("git@github.com:", "")
        owner, repo_name = repo_url.split("/")[:2]
        repo_name = repo_name.replace(".git", "")
    
    return f"{owner}/{repo_name}"

# Immutable. Use this for application configuration. Created at bootstrap.
class GlobalSettings(BaseSettings, Singleton):
    DAGGER: bool = Field(True, env="DAGGER")  
    GITHUB_TOKEN: Optional[SecretStr] = Field(None, env="GITHUB_CUSTOM_TOKEN")
    GIT_CURRENT_REVISION: str = Field(default_factory=get_git_revision)                                                                                                                                  
    GIT_CURRENT_BRANCH: str = Field(default_factory=get_current_branch)                                                                                                                              
    GIT_LATEST_COMMIT_MESSAGE: str = Field(default_factory=get_latest_commit_message)                                                                                                                
    GIT_LATEST_COMMIT_AUTHOR: str = Field(default_factory=get_latest_commit_author)                                                                                                                  
    GIT_LATEST_COMMIT_TIME: str = Field(default_factory=get_latest_commit_time)   
    GIT_REPOSITORY: str = Field(default_factory=get_repo_fullname)       
    GIT_REPO_ROOT_PATH: str = Field(default_factory=get_repo_root_path)
    CI: bool = Field(False, env="CI")
    LOG_LEVEL: str = Field("WARNING", env="LOG_LEVEL")
    PLATFORM: str = platform.system()
    DEBUG: bool = Field(False, env="AIRCMD_DEBUG")

    # https://github.com/actions/toolkit/blob/7b617c260dff86f8d044d5ab0425444b29fa0d18/packages/github/src/context.ts#L6
    GITHUB_EVENT_NAME: str = Field("push", env="GITHUB_EVENT_NAME")
    GITHUB_ACTION: str = Field("local_action", env="GITHUB_ACTION")
    GITHUB_ACTOR: str = Field("local_actor", env="GITHUB_ACTOR")
    GITHUB_JOB: str = Field("local_job", env="GITHUB_JOB")
    GITHUB_RUN_NUMBER: int = Field(0, env="GITHUB_RUN_NUMBER")
    GITHUB_RUN_ID: int = Field(0, env="GITHUB_RUN_ID")
    GITHUB_API_URL: str = Field("https://api.github.com", env="GITHUB_API_URL")
    GITHUB_SERVER_URL: str = Field("https://github.com", env="GITHUB_SERVER_URL")
    GITHUB_GRAPHQL_URL: str = Field("https://api.github.com/graphql", env="GITHUB_GRAPHQL_URL")
    GITHUB_EVENT_PATH: Optional[str] = Field("/tmp/mockevents", env="GITHUB_EVENT_PATH")

    POETRY_CACHE_DIR: str = Field(
        default_factory=lambda: platformdirs.user_cache_dir("pypoetry"),
        env="POETRY_CACHE_DIR"
    )
    MYPY_CACHE_DIR: str = Field("~/.cache/.mypy_cache", env="MYPY_CACHE_DIR")
    DEFAULT_PYTHON_EXCLUDE: List[str] = Field(["**/.venv", "**/__pycache__"], env="DEFAULT_PYTHON_EXCLUDE")
    DEFAULT_EXCLUDED_FILES: List[str] = Field(
        [
            ".git",
            "**/build",
            "**/.venv",
            "**/secrets",
            "**/__pycache__",
            "**/*.egg-info",
            "**/.vscode",
            "**/.pytest_cache",
            "**/.eggs",
            "**/.mypy_cache",
            "**/.DS_Store",
        ],
        env="DEFAULT_EXCLUDED_FILES"
    )
    DOCKER_VERSION:str = Field("20.10.23", env="DOCKER_VERSION")
    DOCKER_DIND_IMAGE: str = Field("docker:dind", env="DOCKER_DIND_IMAGE")
    DOCKER_CLI_IMAGE: str = Field("docker:cli", env="DOCKER_CLI_IMAGE")
    GRADLE_HOMEDIR_PATH: str = Field("/root/.gradle", env="GRADLE_HOMEDIR_PATH")
    GRADLE_CACHE_VOLUME_PATH: str = Field("/root/gradle-cache", env="GRADLE_CACHE_VOLUME_PATH")

    PREFECT_API_URL: str = Field("http://127.0.0.1:4200/api", env="PREFECT_API_URL")
    PREFECT_COMMA_DELIMITED_USER_TAGS: str = Field("", env="PREFECT_COMMA_DELIMITED_USER_TAGS")
    PREFECT_COMMA_DELIMITED_SYSTEM_TAGS: str = Field("CI:False", env="PREFECT_COMMA_DELIMITED_SYSTEM_TAGS")

    SECRET_DOCKER_HUB_USERNAME: Optional[SecretStr] = Field(None, env="SECRET_DOCKER_HUB_USERNAME")
    SECRET_DOCKER_HUB_PASSWORD: Optional[SecretStr] = Field(None, env="SECRET_DOCKER_HUB_PASSWORD")
    SECRET_TAILSCALE_AUTHKEY: Optional[SecretStr] = Field(None, env="SECRET_TAILSCALE_AUTHKEY")
    
    PIP_CACHE_DIR: str = Field(
        default_factory=lambda: platformdirs.user_cache_dir("pip"),
        env="PIP_CACHE_DIR"
    )

    class Config:                                                                                                                                                        
         arbitrary_types_allowed = True                                                                                                                                   
         env_file = '.env' 
         allow_mutation = False


'''
If both include and exclude are supplied, the load_settings function will first filter the environment variables based on the include list, and then it will    
further filter the resulting environment variables based on the exclude list.                                                                                   

Here's the order of operations:                                                                                                                                 

 1 If include is provided, only the environment variables with keys in the include list will be considered.                                                     
 2 If exclude is provided, any environment variables with keys in the exclude list will be removed from the filtered list obtained in step 1.                   
 3 The remaining environment variables will be loaded into the container.   
'''                                                                                                             
                                                                                                                                                                
def load_settings(client: Client, settings: BaseSettings, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Callable[[Container], Container]:     
    def load_envs(ctr: Container) -> Container:                                                                                                                
        settings_dict = {key: value for key, value in settings.dict().items() if value is not None}                                                            
                                                                                                                                                            
        if include is not None:                                                                                                                                
            settings_dict = {key: settings_dict[key] for key in include if key in settings_dict}                                                               
                                                                                                                                                            
        if exclude is not None:                                                                                                                                
            settings_dict = {key: value for key, value in settings_dict.items() if key not in exclude}                                                         
                                                                                                                                                            
        for key, value in settings_dict.items():
            env_key = key.upper()
            if isinstance(value, SecretStr) or isinstance(value, SecretBytes): # env var can be stored in buildkit layer cache, so we must use client.secret instead
                secret = client.set_secret(env_key, str(value.get_secret_value()))
                ctr = ctr.with_secret_variable(env_key, secret)
            else:
                ctr = ctr.with_env_variable(env_key, str(value))
                                                                                                                                                            
        return ctr                                                                                                                                             
                                                                                                                                                        
    return load_envs     


class GithubActionsInputSettings(BaseSettings):
    """
    A Pydantic BaseSettings subclass that transforms input names to the format expected by GitHub Actions.

    GitHub Actions converts input names to environment variables in a specific way:
    - The input name is converted to uppercase.
    - Any '-' characters are converted to '_'.
    - The prefix 'INPUT_' is added to the start.

    This class automatically applies these transformations when you create an instance of it.

    Example:
    If you create an instance with the input {'project-token': 'abc'}, it will be transformed to {'INPUT_PROJECT_TOKEN': 'abc'}.
    """

    # Github action specific fields
    GITHUB_ACTION: str
    GITHUB_ACTOR: str
    GITHUB_API_URL: str
    GITHUB_EVENT_NAME: str
    GITHUB_GRAPHQL_URL: str
    GITHUB_JOB: str
    GITHUB_REF: str
    GITHUB_REPOSITORY: str
    GITHUB_RUN_ID: str
    GITHUB_RUN_NUMBER: str
    GITHUB_SERVER_URL: str
    GITHUB_SHA: str
    GITHUB_EVENT_PATH: str

    class Config:
        env_prefix = "INPUT_"
        extra = "allow" 

    def __init__(self, global_settings: GlobalSettings, **data: Any):

        # transform input names to the format expected by GitHub Actions and prepare them to be injected as environment variables.

        transformed_data = {self.Config.env_prefix + k.replace("-", "_").upper(): v for k, v in data.items()}
        
        # inject the context that github actions wants via environment variables.
        # in typescript, it is injected here:
        # https://github.com/actions/toolkit/blob/7b617c260dff86f8d044d5ab0425444b29fa0d18/packages/github/src/context.ts#L6

        transformed_data.update({
            "GITHUB_SHA": global_settings.GIT_CURRENT_REVISION,
            "GITHUB_REF": global_settings.GIT_CURRENT_BRANCH,
            "GITHUB_EVENT_NAME": global_settings.GITHUB_EVENT_NAME,
            "GITHUB_ACTION": global_settings.GITHUB_ACTION,
            "GITHUB_ACTOR": global_settings.GITHUB_ACTOR,
            "GITHUB_JOB": global_settings.GITHUB_JOB,
            "GITHUB_RUN_NUMBER": global_settings.GITHUB_RUN_NUMBER,
            "GITHUB_RUN_ID": global_settings.GITHUB_RUN_ID,
            "GITHUB_API_URL": global_settings.GITHUB_API_URL,
            "GITHUB_SERVER_URL": global_settings.GITHUB_SERVER_URL,
            "GITHUB_GRAPHQL_URL": global_settings.GITHUB_GRAPHQL_URL,
            "GITHUB_REPOSITORY": global_settings.GIT_REPOSITORY, 
            "GITHUB_EVENT_PATH": global_settings.GITHUB_EVENT_PATH
        })
        super().__init__(**transformed_data)

