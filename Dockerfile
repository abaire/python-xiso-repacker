FROM xboxdev/nxdk:latest

RUN apk update && apk add --no-cache -u \
    python3 \
    py3-pip

RUN mkdir -p /data/TestNXDKPgraphTests
RUN pip install nxdk-pgraph-test-repacker --break-system-packages

WORKDIR /work

ENTRYPOINT ["/bin/env", "python", "-m", "nxdk-pgraph-test-repacker", "-T", "/usr/src/nxdk/tools/extract-xiso/build/extract-xiso"]

