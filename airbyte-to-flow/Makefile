export CARGO_TARGET_X86_64_UNKNOWN_LINUX_MUSL_RUSTFLAGS=-C linker=musl-gcc

target/x86_64-unknown-linux-musl/airbyte-to-flow:
	cargo build --target x86_64-unknown-linux-musl --release --locked
