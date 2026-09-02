FROM alpine:3.22

RUN apk add --no-cache \
    bash \
    tree \
    ripgrep \
    findutils \
    diffutils \
    coreutils \
    patch \
    less

RUN addgroup -S agent && \
    adduser -S -D -h /home/agent -s /bin/bash -G agent agent && \
    mkdir -p /workspace && \
    chown -R agent:agent /workspace

WORKDIR /workspace
USER agent

CMD ["bash"]