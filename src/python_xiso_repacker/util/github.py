from __future__ import annotations

import logging
import os
from os import PathLike
from typing import Any
from urllib.request import urlcleanup, urlretrieve

import requests

logger = logging.getLogger(__name__)


def fetch_github_release_info(api_url: str, tag: str = "latest") -> dict[str, Any] | None:
    full_url = f"{api_url}/releases/latest" if not tag or tag == "latest" else f"{api_url}/releases"

    def fetch_and_filter(url: str):
        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=15,
            )
            response.raise_for_status()
            release_info = response.json()

        except requests.exceptions.RequestException:
            logger.exception("Failed to retrieve information from %s", url)
            return None

        if isinstance(release_info, list):
            release_info = _filter_release_info_by_tag(release_info, tag)
        if release_info:
            return release_info

        if not response.links:
            return None

        next_link = response.links.get("next", {}).get("url")
        if not next_link:
            return None
        next_link = next_link + "&per_page=60"
        return fetch_and_filter(next_link)

    return fetch_and_filter(full_url)


def _download_url(download_url: str, target_path: str | PathLike) -> bool:
    """Downloads a file from a URL to a local target path, creating parent directories."""
    if not download_url.startswith("https://"):
        logger.error("Download URL '%s' has unexpected scheme", download_url)
        msg = f"Bad download_url '{download_url}' - non HTTPS scheme"
        raise ValueError(msg)

    target_path_str = str(target_path)
    output_dir = os.path.dirname(os.path.abspath(target_path_str))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    logger.debug("Downloading %s from %s", target_path_str, download_url)
    urlretrieve(download_url, target_path_str)  # noqa: S310 - checked just above
    urlcleanup()
    return True


def download_artifact(
    target_path: str, download_url: str, artifact_path_override: str | None = None, *, force_download: bool = False
) -> bool:
    """Downloads an artifact from the given URL, if it does not already exist. Returns True if download was needed."""
    if os.path.exists(target_path) and not force_download:
        return False

    if artifact_path_override and os.path.exists(artifact_path_override) and not force_download:
        return True

    destination = artifact_path_override if artifact_path_override else target_path
    if artifact_path_override:
        logger.debug(
            "> downloading artifact %s containing %s",
            artifact_path_override,
            target_path,
        )

    return _download_url(download_url, destination)


def download_github_release_asset(
    api_url: str,
    output_path: str | PathLike,
    *,
    name_contains: str | None = None,
    name_ends_with: str | None = None,
    tag: str = "latest",
) -> bool:
    """Downloads an asset from a GitHub release matching specified criteria."""
    info = fetch_github_release_info(api_url, tag=tag)
    if not info:
        return False

    download_url = ""
    for asset in info.get("assets", []):
        name: str = asset.get("name", "")
        if name_ends_with and not name.endswith(name_ends_with):
            continue
        if name_contains and name_contains not in name:
            continue
        download_url = asset.get("browser_download_url", "")
        break

    if not download_url:
        logger.error("Failed to fetch download URL for release from %s", api_url)
        return False

    try:
        return _download_url(download_url, output_path)
    except ValueError:
        return False


def _filter_release_info_by_tag(release_infos: list[dict[str, Any]], tag: str) -> dict[str, Any] | None:
    for info in release_infos:
        if info.get("tag_name") == tag:
            return info
    return None
