from typing import List
from pipelines.utils import sh_dash_c


from dagger import Container


def with_git(dagger_client, ci_github_access_token_secret, ci_git_user) -> Container:
    return (
        dagger_client.container()
        .from_("alpine:latest")
        .with_exec(
            sh_dash_c(
                [
                    "apk update",
                    "apk add git tar wget",
                    f"git config --global user.email {ci_git_user}@users.noreply.github.com",
                    f"git config --global user.name {ci_git_user}",
                    "git config --global --add --bool push.autoSetupRemote true",
                ]
            )
        )
        .with_secret_variable("GITHUB_TOKEN", ci_github_access_token_secret)
        .with_workdir("/ghcli")
        .with_exec(
            sh_dash_c(
                [
                    "wget https://github.com/cli/cli/releases/download/v2.30.0/gh_2.30.0_linux_amd64.tar.gz -O ghcli.tar.gz",
                    "tar --strip-components=1 -xf ghcli.tar.gz",
                    "rm ghcli.tar.gz",
                    "cp bin/gh /usr/local/bin/gh",
                ]
            )
        )
    )


def with_alpine_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using apk-get.
    Args:
        context (Container): A alpine based container.

    Returns:
        Container: A container with the packages installed.

    """
    package_install_command = ["apk", "add"]
    return base_container.with_exec(package_install_command + packages_to_install)


