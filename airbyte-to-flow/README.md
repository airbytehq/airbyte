# Build

```
make && docker buildx build --platform linux/amd64 -t ghcr.io/estuary/airbyte-to-flow:local --push .
```

# Building on M1

Before running make, set this environment variable:
```
export CARGO_TARGET_X86_64_UNKNOWN_LINUX_MUSL_RUSTFLAGS="-C linker=musl-gcc"
```
