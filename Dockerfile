FROM xboxdev/nxdk:latest

RUN apk update && apk add --no-cache -u \
    python3 \
    py3-pip \
    py3-virtualenv \
    ;

RUN mkdir -p /data/TestNXDKPgraphTests

RUN /usr/bin/python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip3 install nxdk-pgraph-test-repacker

WORKDIR /work

ENTRYPOINT ["/venv/bin/python3", "-m", "nxdk_pgraph_test_repacker", "-T", "/usr/src/nxdk/tools/extract-xiso/build/extract-xiso"]

