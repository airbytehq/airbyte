# Introduction

Building locally:

This command will build the image ghcr.io/estuary/source-intercom:local
```
./local-build.sh source-intercom
```

You can then use `flowctl-go` commands to inspect the connector
e.g. to check the spec

```
flowctl-go api spec --image ghcr.io/estuary/source-intercom:local | jq
```

You can now modify patches, etc. and then re-run the commands
to build and check the spec

```
./local-build.sh source-intercom
flowctl-go api spec --image ghcr.io/estuary/source-intercom:local | jq
```

To check the discovered bindings of a connector, you can use
`flowctl-go discover`

```
flowctl-go discover --image ghcr.io/estuary/source-intercom:local
```

Fill in the config file at `acmeCo/source-intercom.config.yaml`
and run discover again

```
flowctl-go discover --image ghcr.io/estuary/source-intercom:local
```

You can now check the discovered bindings in `acmeCo` and make sure that
the discovered bindings match your expectations

## airbyte-to-flow

See the README file in `airbyte-to-flow` directory.
