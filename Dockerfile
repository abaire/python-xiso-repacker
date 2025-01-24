FROM xboxdev/nxdk:latest

RUN apk update && apk add --no-cache -u \
    bash \
    jq \
    curl \
    libcurl

RUN mkdir -p /data/TestNXDKPgraphTests
COPY --chmod=0770 entrypoint.sh /bin/nxdk-pgraph-test-repacker.sh

WORKDIR /work

ENV PATH="${PATH}:/usr/src/nxdk/tools/extract-xiso/build/"

ENTRYPOINT ["/bin/nxdk-pgraph-test-repacker.sh"]
