## Building

These connectors are based on `source-criteo`/`source-kelkoo` from `gjbakerross`. The upstream sources including `Dockerfile` can be found here:
* https://github.com/gjbakerross/airbyte-source-criteo
* https://github.com/gjbakerross/airbyte-source-kelkoo

We build those repositories and push the artifacts to `ghcr.io/estuary/gjbakerross/source-criteo`/`source-kelkoo` with the following command:

```
docker buildx build --no-cache --platform linux/amd64 https://github.com/gjbakerross/airbyte-source-criteo.git -t ghcr.io/estuary/gjbakerross/source-criteo:dev --push
```