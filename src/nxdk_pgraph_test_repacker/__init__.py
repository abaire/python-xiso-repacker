# SPDX-FileCopyrightText: 2025-present Erik Abair <erik.abair@bearbrains.work>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import glob
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from os import PathLike
from typing import Any
from urllib.request import urlcleanup, urlretrieve

import requests
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)

_NXDK_PGRAPH_TESTS_REPO_API = "https://api.github.com/repos/abaire/nxdk_pgraph_tests"
_EXTRACT_XISO_REPO_API = "https://api.github.com/repos/XboxDev/extract-xiso"

_NXDK_PGRAPH_TESTS_CONFIG_FILE = "nxdk_pgraph_tests_config.json"


def _fetch_release_info(api_url: str, tag: str = "latest") -> dict[str, Any] | None:
    full_url = f"{api_url}/releases/{tag}"
    try:
        logging.debug("Fetching info via GitHub API")
        response = requests.get(
            full_url,
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception("Failed to retrieve information from %s", full_url)
        return None


def download_latest_iso(output_path: str | PathLike) -> bool:
    """Downloads the latest nxdk_pgraph_tests xiso."""
    logging.info("Downloading latest nxdk_pgraph_tests xiso...")

    info = _fetch_release_info(_NXDK_PGRAPH_TESTS_REPO_API)
    if not info:
        return False

    download_url = ""
    for asset in info.get("assets", []):
        if not asset.get("name", "").endswith(".iso"):
            continue
        download_url = asset.get("browser_download_url", "")
        break

    if not download_url:
        logger.error("Failed to fetch download URL for latest nxdk_pgraph_tests release")
        return False

    if not download_url.startswith("https://"):
        logger.error("Download URL '%s' has unexpected scheme", download_url)
        return False

    urlretrieve(download_url, output_path)  # noqa: S310 - checked just above
    urlcleanup()

    return True


def _download_latest_extract_xiso(output_path: str) -> bool:
    logging.info("Downloading latest extract-xiso release...")
    info = _fetch_release_info(_EXTRACT_XISO_REPO_API)
    if not info:
        return False

    system_name = platform.system()
    if system_name == "Darwin":
        asset_name = "macOS"
    elif system_name == "Linux":
        asset_name = "Linux"
    else:
        msg = f"Unsupported host system '{system_name}'"
        raise NotImplementedError(msg)

    download_url = ""
    for asset in info.get("assets", []):
        name: str = asset.get("name", "")
        if not name.endswith(".zip"):
            continue

        if asset_name in name:
            download_url = asset.get("browser_download_url", "")
            break

    if not download_url:
        logger.error("Failed to fetch download URL for latest extract-xiso release with platform %s", asset_name)
        return False

    zip_path = f"{output_path}.zip"
    if not download_url.startswith("https://"):
        logger.error("Download URL '%s' has unexpected scheme", download_url)
        return False
    urlretrieve(download_url, zip_path)  # noqa: S310 - checked just above
    urlcleanup()

    logging.debug("Extracting binary from zip file at %s", zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            filename = member.filename
            if filename != "extract-xiso":
                continue

            with open(output_path, "wb") as outfile:
                outfile.write(archive.read(member))

            os.chmod(output_path, 0o700)

    return True


def _ensure_extract_xiso(path_hint: str) -> str | None:
    allow_download = False
    if not path_hint:
        output_dir = user_data_dir("nxdk-pgraph-test-repacker")
        os.makedirs(output_dir, exist_ok=True)
        path_hint = os.path.join(output_dir, "extract-xiso")
        allow_download = True

    if os.path.isfile(path_hint):
        return path_hint

    on_path = shutil.which(path_hint)
    if on_path:
        return on_path

    if not allow_download:
        return None

    if not _download_latest_extract_xiso(path_hint):
        return None

    return path_hint


def _ensure_output_directory(output: str) -> str:
    if os.path.isdir(output) or not output.endswith(".iso"):
        output = os.path.join(output, "nxdk_pgraph_tests_xiso-updated.iso")

    output_dirname = os.path.dirname(output)
    if output_dirname:
        os.makedirs(output_dirname, exist_ok=True)

    return output


def repack_config(iso_file: str, output_file: str, config_file: str, extract_xiso_binary: str) -> int:
    logger.info("Repacking config in %s from %s using %s", iso_file, config_file, extract_xiso_binary)

    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run([extract_xiso_binary, "-d", tmpdir, "-x", iso_file], capture_output=True, check=False)

        shutil.copy(config_file, os.path.join(tmpdir, _NXDK_PGRAPH_TESTS_CONFIG_FILE))

        subprocess.run([extract_xiso_binary, "-c", tmpdir, output_file], capture_output=True, check=False)
        logger.info("Generated %s", output_file)

    return 0


def extract_config(iso_file: str, output_file: str, extract_xiso_binary: str) -> int:
    logger.info("Extracting config from %s using %s", iso_file, extract_xiso_binary)

    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run([extract_xiso_binary, "-d", tmpdir, "-x", iso_file], capture_output=True, check=False)

        accepted_config_file = ""
        for config_file in glob.glob(os.path.join(tmpdir, "*.json")):
            accepted_config_file = config_file

            # Prefer the file that actually has an effect, but accept any JSON file.
            if os.path.basename(config_file) == _NXDK_PGRAPH_TESTS_CONFIG_FILE:
                break

        if not accepted_config_file:
            return 100

        logger.info("Retrieved %s", os.path.basename(accepted_config_file))
        shutil.copy(accepted_config_file, output_file)
        return 0


def run():
    """Parses program arguments and executes the repacker."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enables verbose logging information",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Path to where the reconfigured xiso should be saved",
        default="nxdk_pgraph_tests_xiso-updated.iso",
    )
    parser.add_argument("--extract-xiso-tool", "-T", help="Path to the extract-xiso tool")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--download",
        "-d",
        default="nxdk_pgraph_tests_xiso-latest.iso",
        help="Download the latest nxdk_pgraph_tests xiso",
    )
    source.add_argument("--iso", "-i", help="Path to an existing nxdk_pgraph_tests xiso file to reconfigure")

    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--config", "-c", metavar="config_json_filepath", help="Path to the new JSON config to inject into the xiso"
    )
    action.add_argument(
        "--extract-config",
        "-e",
        metavar="extracted_config_filepath",
        help="Extract the existing config from the xiso instead of repacking",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    output = _ensure_output_directory(args.output)

    if args.iso:
        iso_file = args.iso
    else:
        if not download_latest_iso(args.download):
            sys.exit(1)
        iso_file = args.download

    if not os.path.isfile(iso_file):
        logger.error("Input ISO '%s' not found!", iso_file)
        sys.exit(2)

    if not (args.config or args.extract_config):
        sys.exit(0)

    extract_xiso = _ensure_extract_xiso(args.extract_xiso_tool)
    if not extract_xiso:
        logger.error("extract-xiso tool not found")
        sys.exit(3)

    if args.config:
        sys.exit(repack_config(iso_file, output, args.config, extract_xiso))
    elif args.extract_config:
        sys.exit(extract_config(iso_file, args.extract_config, extract_xiso))
