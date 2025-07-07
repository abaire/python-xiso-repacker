from __future__ import annotations

import logging
import os
import platform
import shutil
import zipfile
from os import PathLike
from urllib.request import urlcleanup, urlretrieve

from platformdirs import user_data_dir

from python_xiso_repacker.util.github import fetch_github_release_info

logger = logging.getLogger(__name__)

_EXTRACT_XISO_REPO_API = "https://api.github.com/repos/XboxDev/extract-xiso"


def _download_latest_extract_xiso(output_path: str | PathLike) -> bool:
    logger.info("Downloading latest extract-xiso release...")
    info = fetch_github_release_info(_EXTRACT_XISO_REPO_API)
    if not info:
        return False

    system_name = platform.system()
    if system_name == "Darwin":
        asset_name = "macOS"
    elif system_name == "Linux":
        asset_name = "Linux"
    elif system_name == "Windows":
        asset_name = "Win64_Release"
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

    logger.debug("Extracting binary from zip file at %s", zip_path)
    binary_name = "extract-xiso.exe" if system_name == "Windows" else "extract-xiso"
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            if not member.filename.endswith(binary_name) or member.is_dir():
                continue

            output_dir = os.path.dirname(output_path)
            archive.extract(member, output_dir)
            os.rename(os.path.join(output_dir, member.filename), output_path)
            os.chmod(output_path, 0o700)
            return True

    logger.error("Failed to find extract-xiso binary within zip file at %s", zip_path)
    return False


def ensure_extract_xiso(path_hint: str | None) -> str | None:
    """Ensures that the extract-xiso program is available and returns its path.

    :param path_hint - Path at which the extract-xiso program is expected to be

    :return The full path of extract-xiso or None if it was not found.
    """
    allow_download = False
    if not path_hint:
        output_dir = user_data_dir("python-xiso-repacker")
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
