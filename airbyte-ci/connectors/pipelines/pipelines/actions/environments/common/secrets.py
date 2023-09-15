from pipelines.contexts import PipelineContext


from dagger import Container


from typing import Callable


async def mounted_connector_secrets(context: PipelineContext, secret_directory_path: str) -> Callable[[Container], Container]:
    # By default, mount the secrets properly as dagger secret files.
    #
    # This will cause the contents of these files to be scrubbed from the logs. This scrubbing comes at the cost of
    # unavoidable latency in the log output, see next paragraph for details as to why. This is fine in a CI environment
    # however this becomes a nuisance locally: the developer wants the logs to be displayed to them in an as timely
    # manner as possible. Since the secrets aren't really secret in that case anyway, we mount them in the container as
    # regular files instead.
    #
    # The buffering behavior that comes into play when logs are scrubbed is both unavoidable and not configurable.
    # It's fundamentally unavoidable because dagger needs to match a bunch of regexes (one per secret) and therefore
    # needs to buffer at least as many bytes as the longest of all possible matches. Still, this isn't that long in
    # practice in our case. The real problem is that the buffering is not configurable: dagger relies on a golang
    # library called transform [1] to perform the regexp matching on a stream and this library hard-codes a buffer
    # size of 4096 bytes for each regex [2].
    #
    # Remove the special local case whenever dagger implements scrubbing differently [3,4].
    #
    # [1] https://golang.org/x/text/transform
    # [2] https://cs.opensource.google/go/x/text/+/refs/tags/v0.13.0:transform/transform.go;l=130
    # [3] https://github.com/dagger/dagger/blob/v0.6.4/cmd/shim/main.go#L294
    # [4] https://github.com/airbytehq/airbyte/issues/30394
    #
    if context.is_local:
        # Special case for local development.
        # Query dagger for the contents of the secrets and mount these strings as files in the container.
        contents = {}
        for secret_file_name, secret in context.connector_secrets.items():
            contents[secret_file_name] = await secret.plaintext()

        def with_secrets_mounted_as_regular_files(container: Container) -> Container:
            container = container.with_exec(["mkdir", secret_directory_path], skip_entrypoint=True)
            for secret_file_name, secret_content_str in contents.items():
                container = container.with_new_file(f"{secret_directory_path}/{secret_file_name}", secret_content_str, permissions=0o600)
            return container

        return with_secrets_mounted_as_regular_files

    def with_secrets_mounted_as_dagger_secrets(container: Container) -> Container:
        container = container.with_exec(["mkdir", secret_directory_path], skip_entrypoint=True)
        for secret_file_name, secret in context.connector_secrets.items():
            container = container.with_mounted_secret(f"{secret_directory_path}/{secret_file_name}", secret)
        return container

    return with_secrets_mounted_as_dagger_secrets
