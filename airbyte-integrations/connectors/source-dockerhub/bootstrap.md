# Dockerhub Source API

- Origin issue/discussion: https://github.com/airbytehq/airbyte/issues/12773
- API docs: https://docs.docker.com/registry/spec/api/
- Helpful StackOverflow answer on DockerHub API auth call: https://stackoverflow.com/questions/56193110/how-can-i-use-docker-registry-http-api-v2-to-obtain-a-list-of-all-repositories-i#answer-68654659

All API calls need to be authenticated, but for public info, you can just obtain a short lived token from [this endpoint](https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull) without any username/password, so is what we have done.