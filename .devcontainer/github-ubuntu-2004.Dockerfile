# This Dockerfile is a facsimile of the "ubuntu-2004" GitHub action runner,
# trimmed down to those software packages which we actually use.
# https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-Readme.md
#
# Don't install anything in this Dockerfile which isn't also present in that environment!
# Instead, further packages must be installed through explicit build steps.
# This practice keeps builds within devcontainer environments (i.e. codespaces) in lock-step
# with what works in GitHub Actions CI.
FROM ubuntu:20.04

## Set a configured locale.
ARG LOCALE=en_US.UTF-8

# See the package list in the GitHub reference link above, at the very bottom,
# which lists installed apt packages.
RUN apt update -y \
    && apt upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y \
    bash-completion \
    build-essential \
    ca-certificates \
    clang-12 \
    cmake \
    curl \
    docker-compose \
    docker.io \
    git \
    gnupg2 \
    iproute2 \
    jq \
    less \
    libclang-12-dev \
    libssl-dev \
    lld-12 \
    locales \
    musl-tools \
    net-tools \
    netcat \
    pkg-config \
    psmisc \
    strace \
    sudo \
    tcpdump \
    unzip \
    vim-tiny \
    wget \
    zip

RUN locale-gen ${LOCALE}

## Install Rust. This is pasted from:
## https://github.com/rust-lang/docker-rust/blob/master/1.64.0/bullseye/Dockerfile
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.64.0 \
    RUST_TARGET=x86_64-unknown-linux-musl

RUN set -eux; \
    dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
    amd64) rustArch='x86_64-unknown-linux-gnu'; rustupSha256='5cc9ffd1026e82e7fb2eec2121ad71f4b0f044e88bca39207b3f6b769aaa799c' ;; \
    armhf) rustArch='armv7-unknown-linux-gnueabihf'; rustupSha256='48c5ecfd1409da93164af20cf4ac2c6f00688b15eb6ba65047f654060c844d85' ;; \
    arm64) rustArch='aarch64-unknown-linux-gnu'; rustupSha256='e189948e396d47254103a49c987e7fb0e5dd8e34b200aa4481ecc4b8e41fb929' ;; \
    i386) rustArch='i686-unknown-linux-gnu'; rustupSha256='0e0be29c560ad958ba52fcf06b3ea04435cb3cd674fbe11ce7d954093b9504fd' ;; \
    *) echo >&2 "unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac; \
    url="https://static.rust-lang.org/rustup/archive/1.25.1/${rustArch}/rustup-init"; \
    wget "$url"; \
    echo "${rustupSha256} *rustup-init" | sha256sum -c -; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --profile minimal --default-toolchain $RUST_VERSION \
    --default-host ${rustArch} --target $RUST_TARGET; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; \
    cargo --version; \
    rustc --version;

# The above copy-paste installed the "minimal" profile, but GitHub runners
# feature additional tools.
# See: https://blog.rust-lang.org/2019/10/15/Rustup-1.20.0.html#profiles
RUN rustup set profile default \
    && rustup component add clippy rustfmt rust-docs

# Add `flow` user with sudo access.
RUN useradd flow --create-home --shell /bin/bash \
    && echo flow ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/flow \
    && chmod 0440 /etc/sudoers.d/flow

# Adapted from: https://github.com/microsoft/vscode-dev-containers/tree/main/containers/docker-from-docker#adding-the-user-to-a-docker-group
COPY docker-debian.sh /tmp
RUN bash /tmp/docker-debian.sh true /var/run/docker-host.sock /var/run/docker.sock flow false

# VS Code overrides ENTRYPOINT and CMD when executing `docker run` by default.
# Setting the ENTRYPOINT to docker-init.sh will configure non-root access to
# the Docker socket if "overrideCommand": false is set in devcontainer.json.
# The script will also execute CMD if you need to alter startup behaviors.
ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]
