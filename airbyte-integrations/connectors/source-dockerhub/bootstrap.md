# Dockerhub Source API

- Origin issue/discussion: https://github.com/airbytehq/airbyte/issues/12773
- API docs: https://docs.docker.com/registry/spec/api/
- Helpful StackOverflow answer on DockerHub API auth call: https://stackoverflow.com/questions/56193110/how-can-i-use-docker-registry-http-api-v2-to-obtain-a-list-of-all-repositories-i#answer-68654659

All API calls need to be authenticated, but for public info, you can just obtain a short lived token from [this endpoint](https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull) without any username/password, so this is what we have done for simplicity.

If you are reading this in the future and need to expand this source connector to include private data, do take note that you'll need to add the `/secrets/config.json` files and change the auth strategy (we think it takes either HTTP basic auth or Oauth2 to the same endpoint, with the right scope):

- Original notes: https://github.com/airbytehq/airbyte/issues/12773#issuecomment-1126785570
- Auth docs: https://docs.docker.com/registry/spec/auth/jwt/
- Might also want to use OAuth2: https://docs.docker.com/registry/spec/auth/oauth/
- Scope docs: https://docs.docker.com/registry/spec/auth/scope/
