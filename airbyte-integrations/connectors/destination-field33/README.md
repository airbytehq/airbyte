# Field 33 Destination

This is the repository for the Field 33 destination connector, written in Rust.
This connector is currently in the alpha stage.

## Local development

You will need an working Rust installation. We recommend using [RustUp](https://rustup.rs).

Build and test normally with `cargo`:

```
cargo build
cargo test
cargo run -- spec
cargo run -- check --config path-to-config.json
cargo run -- write --config path-to-config.json --catalog path-to-catalog.json
```

