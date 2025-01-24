# nxdk-pgraph-test-repacker

-----

## Purpose

Simple Docker-based solution to fetch and reconfigure
the [nxdk_pgraph_tests](https://github.com/abaire/nxdk_pgraph_tests) xiso.

### Prerequisites

* Docker - required

## Usage

The image will operate on the `work` volume, so it should be mounted in order to
provide inputs and retrieve created artifacts.

### Build the image

```shell
DOCKER_BUILDKIT=1 docker build -t nxdk-pgraph-test-repacker .
````

### Examples

* Download the latest nxdk_pgraph_images ISO image to
  `output/latest_nxdk_pgraph_tests_xiso.iso`

    ```shell
    docker run --rm -it \
    -v "${PWD}/output":/work \
    nxdk-pgraph-test-repacker \
    --download
    ```
* Update a previously retrieved ISO called `data/clean_nxdk_pgraph_tests.iso`
  with a config named `data/config.json`, writing to
  `data/nxdk_pgraph_tests_xiso-updated.iso`

    ```shell
    docker run --rm -it \
    -v "${PWD}/data":/work \
    nxdk-pgraph-test-repacker \
    --iso clean_nxdk_pgraph_tests.iso \
    --config config.json
    ```
