# nxdk-pgraph-test-repacker

[![PyPI - Version](https://img.shields.io/pypi/v/nxdk-pgraph-test-repacker.svg)](https://pypi.org/project/nxdk-pgraph-test-repacker)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nxdk-pgraph-test-repacker.svg)](https://pypi.org/project/nxdk-pgraph-test-repacker)

-----

## Purpose

A simple tool to reconfigure
the [nxdk_pgraph_tests xiso](https://github.com/abaire/nxdk_pgraph_tests),
suitable for use in automated testing.

## Installation

```console
pip install nxdk-pgraph-test-repacker
```

## Usage

```console
python -m nxdk_pgraph_test_repacker -h
```

### Docker

```console
docker pull ghcr.io/abaire/nxdk-pgraph-test-repacker:latest
```

To download the latest nxdk_pgraph_tests image to
output/latest_nxdk_pgraph_tests_xiso.iso:

```console
docker run --rm -it \
    -v "${PWD}/output":/work \
    nxdk-pgraph-test-repacker \
    --download
```

To update a previously retrieved ISO called `data/clean_nxdk_pgraph_tests.iso`
using a new config named `data/config.json` and write to
`data/nxdk_pgraph_tests_xiso-updated.iso`:

```console
docker run --rm -it \
    -v "${PWD}/data":/work \
    nxdk-pgraph-test-repacker \
    --iso clean_nxdk_pgraph_tests.iso \
    --config config.json
```

## License

`nxdk-pgraph-test-repacker` is distributed under the terms of
the [MIT](https://spdx.org/licenses/MIT.html) license.
