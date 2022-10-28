ARG ALPINE_IMAGE=alpine:3.16
FROM ${ALPINE_IMAGE} AS kubectl

ENV APPLICATION airbyte-kubectl
ARG VERSION=0.40.17
ARG KUBECTL_VERSION=v1.25.3
ARG DOCKER_BUILD_ARCH
ARG TARGETARCH


# Nginx config file
WORKDIR /

# Install awscli, curl, jq yq
RUN apk add curl jq yq bash --no-cache aws-cli coreutils

RUN export -p; \
    arch=${TARGETARCH:-${DOCKER_BUILD_ARCH:-}} ; \
    arch=${arch:-$(uname -m)} ; \
    arch=${arch/aarch64/amd64} ; \
    kube_url="https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${DOCKER_BUILD_ARCH}/kubectl"; \
    echo $kube_url; \
    curl --fail -sSLO $kube_url && \
    [ -s kubectl ] && \
    chmod +x kubectl && \
    mv kubectl /usr/bin

USER 1001
ENTRYPOINT [ "kubectl" ]
CMD [ "--help" ]
