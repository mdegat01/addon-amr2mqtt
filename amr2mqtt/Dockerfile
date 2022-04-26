ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base/amd64

# https://hub.docker.com/_/alpine
FROM alpine:3.15.4 as build_rtlamr
# https://github.com/bemasher/rtlamr/releases
ENV RTLAMR_VERSION 0.9.1

RUN set -eux; \
    apk update; \
        apk add --no-cache --virtual .build-deps \
            tar=1.34-r0 \
            curl=7.80.0-r0 \
        ; \
    APKARCH="$(apk --print-arch)"; \
    case "${APKARCH}" in \
        x86_64)  BINARCH='amd64' ;; \
        armhf)   BINARCH='arm' ;; \
        armv7)   BINARCH='arm' ;; \
        aarch64) BINARCH='arm64' ;; \
        *) echo >&2 "error: unsupported architecture (${APKARCH})"; exit 1 ;; \
    esac; \
    curl -J -L -o /tmp/rtlamr.tar.gz \
    "https://github.com/bemasher/rtlamr/releases/download/v${RTLAMR_VERSION}/rtlamr_linux_${BINARCH}.tar.gz"; \
    tar -xf /tmp/rtlamr.tar.gz -C /usr/bin; \
    chmod a+x /usr/bin/rtlamr; \
    rm /tmp/rtlamr.tar.gz;

# https://github.com/hassio-addons/addon-debian-base/releases
FROM ${BUILD_FROM}:5.3.1

RUN set -eux; \
    apt-get update; \
    apt-get install -qy --no-install-recommends \ 
        ca-certificates=20210119 \
        librtlsdr-dev=0.6.0-3 \
        python3-paho-mqtt=1.5.1-1 \
        python3-dateutil=2.8.1-6 \
        rtl-sdr=0.6.0-3 \
        ; \
    update-ca-certificates; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*; \
    \
    echo "Add user for AMR2MQTT"; \
    mkdir -p /data/amr2mqtt; \
    useradd -u 12345 -U -d /data/amr2mqtt abc;

# Add rtlamr
COPY --from=build_rtlamr /usr/bin/rtlamr /usr/bin/rtlamr
RUN rtlamr --version

COPY rootfs /
WORKDIR /data/amr2mqtt

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Set name & version as env for use in scripts
ENV BUILD_VERSION=${BUILD_VERSION}
ENV BUILD_NAME=${BUILD_NAME}

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="mdegat01" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="mdegat01's Home Assistant Add-ons" \
    org.opencontainers.image.authors="mdegat01" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/mdegat01/hassio-addons" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
