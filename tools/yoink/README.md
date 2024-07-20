# The Yoink Tool

Yoink tool contains tools to grab connectors from the Cloud Manifests table in prod database
and make manifest-only connectors out of them.

> [!note]
> Not using `connector-commons` to move quickly.

## Usage

### Make a single connector from manifest

```bash
yoink shiny path-to-manifest.yaml
```

### Make multiple connectors from manifest

```bash
yoink hoard --help
```

## Caveats

- Assumes there is only one allowed host (does not walk over all hosts in all streams)

## TODO

- [ ] Improve README template with links to connector development docs
- [ ] Add manifest description to Builder and low-code CDK
