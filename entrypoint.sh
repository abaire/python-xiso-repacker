#!/usr/bin/env bash

set -eu
set -o pipefail

nxdk_pgraph_tests_repo_api=https://api.github.com/repos/abaire/nxdk_pgraph_tests
readonly nxdk_pgraph_tests_repo_api

downloaded_iso_name=latest_nxdk_pgraph_tests_xiso.iso
readonly downloaded_iso_name

updated_iso_name=nxdk_pgraph_tests_xiso-updated.iso
readonly updated_iso_name

function print_help_and_exit() {
  echo "Usage: $0 <option ...>"
  echo ""
  echo "Options:"
  echo "  --help          - Print this message"
  echo "  --download      - Download the latest nxdk_pgraph_tests ISO"
  echo "  --iso <file>    - Use the given nxdk_pgraph_tests ISO"
  echo "  --config <file> - Repack the ISO with the given nxdk_pgraph_tests_config.json"
  exit 1
}

function download_latest_iso() {
  echo "Fetching info on latest nxdk_pgraph_tests ISO..."
  iso_url=$(
    curl -s \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "${nxdk_pgraph_tests_repo_api}/releases/latest" |
      jq -r '.assets[] | select(.name | contains(".iso")).browser_download_url'
  )

  echo "Downloading from ${iso_url}..."
  rm -f "${downloaded_iso_name}"
  curl -s -L "${iso_url}" --output "${downloaded_iso_name}"

  iso="${downloaded_iso_name}"
}

function repack_config() {
  local iso
  iso="${1}"
  local config
  config="${2}"

  echo "Repacking ${iso} with config from ${config}"

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir}"' EXIT

  extract-xiso -d "${tmpdir}" -x "${iso}" >/dev/null

  cp "${config}" "${tmpdir}/nxdk_pgraph_tests_config.json"

  extract-xiso -c "${tmpdir}" "${updated_iso_name}" >/dev/null
}

function main() {
  local fetch_latest
  fetch_latest=false
  local iso
  iso=""
  local config
  config=""

  set +u
  while [ ! -z "${1}" ]; do
    case "${1}" in
    '--download'*)
      fetch_latest=true
      shift
      ;;
    '--iso'*)
      iso="${2}"
      shift 2
      ;;
    '--config'*)
      config="${2}"
      shift 2
      ;;
    '-h'*)
      print_help_and_exit
      ;;
    '-?'*)
      print_help_and_exit
      ;;
    '--help'*)
      print_help_and_exit
      ;;
    *)
      echo "Ignoring unknown option '${1}'"
      break
      ;;
    esac
  done
  set -u

  if [[ ${fetch_latest} == true ]]; then
    if [[ ${iso:+x} == "x" ]]; then
      echo "Error: --download and --iso are mutually exclusive."
      exit 1
    fi
    download_latest_iso
  fi

  if [[ ${iso:+x} != "x" ]]; then
    echo "No ISO specified, exiting."
    exit 1
  fi

  if [[ ${config:+x} == "x" ]]; then
    repack_config "${iso}" "${config}"
  fi
}

main "$@"
