# SPDX-FileCopyrightText: 2025-present Erik Abair <erik.abair@bearbrains.work>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from python_xiso_repacker import _copy_file, extract_file, replace_file, run
from python_xiso_repacker.util.extract_xiso import _download_latest_extract_xiso, ensure_extract_xiso
from python_xiso_repacker.util.github import download_artifact, download_github_release_asset


def test_download_works(tmp_path):
    output_file = tmp_path / "extract-xiso"

    assert _download_latest_extract_xiso(output_file)
    assert os.path.isfile(output_file)


def test_ensure_extract_xiso_with_path(tmp_path):
    fake_tool = tmp_path / "fake-extract-xiso"
    fake_tool.write_text("fake binary")

    found = ensure_extract_xiso(str(fake_tool))
    assert found == str(fake_tool)


def test_ensure_extract_xiso_default_param():
    with patch("python_xiso_repacker.util.extract_xiso.shutil.which", return_value="/usr/bin/extract-xiso"):
        found = ensure_extract_xiso()
        assert found is not None


def test_replace_file(tmp_path):
    iso_file = tmp_path / "test_input.iso"
    iso_file.write_text("fake iso")
    output_file = tmp_path / "test_output.iso"
    replacement_file = tmp_path / "test_new_file.txt"
    replacement_file.write_text("hello world")

    def mock_subprocess_run(*_args, **_kwargs):
        return MagicMock(returncode=0)

    with patch("python_xiso_repacker.subprocess.run", side_effect=mock_subprocess_run):
        assert replace_file(str(iso_file), str(output_file), "some/dir/file.txt", str(replacement_file), "extract-xiso")


def test_extract_file(tmp_path):
    iso_file = tmp_path / "test_extract_input.iso"
    iso_file.write_text("fake iso")
    output_file = tmp_path / "test_extracted.txt"

    def mock_subprocess_run(cmd, *_args, **_kwargs):
        tmpdir = cmd[2]
        extracted = os.path.join(tmpdir, "some/file.txt")
        os.makedirs(os.path.dirname(extracted), exist_ok=True)
        with open(extracted, "w") as f:
            f.write("extracted content")
        return MagicMock(returncode=0)

    with patch("python_xiso_repacker.subprocess.run", side_effect=mock_subprocess_run):
        assert extract_file(str(iso_file), "some/file.txt", str(output_file), "extract-xiso")
        assert output_file.read_text() == "extracted content"


def test_copy_file(tmp_path):
    src = tmp_path / "test_copy_src.txt"
    dst = tmp_path / "test_nested_dir" / "sub" / "test_copy_dst.txt"
    src.write_text("content to copy")

    _copy_file(str(src), str(dst))
    assert dst.is_file()
    assert dst.read_text() == "content to copy"


def test_run_missing_iso():
    with pytest.raises(SystemExit) as exc:
        run(["nonexistent.iso", "file.txt", "-r", "replacement.txt"])
    assert exc.value.code == 2


def test_download_artifact_and_asset(tmp_path):
    with (
        patch("python_xiso_repacker.util.github.urlretrieve") as mock_retrieve,
        patch("python_xiso_repacker.util.github.fetch_github_release_info") as mock_info,
    ):
        target = str(tmp_path / "test_download_art.iso")
        assert download_artifact(target, "https://example.com/file.iso", force_download=True)
        mock_retrieve.assert_called_with("https://example.com/file.iso", target)

        with pytest.raises(ValueError):  # noqa: PT011
            download_artifact(target, "http://insecure.com/file.iso", force_download=True)

        mock_info.return_value = {
            "assets": [
                {"name": "test_asset.zip", "browser_download_url": "https://example.com/test_asset.zip"},
                {"name": "test_other.iso", "browser_download_url": "https://example.com/test_other.iso"},
            ]
        }
        assert download_github_release_asset(
            "https://api.github.com/repos/foo/bar",
            str(tmp_path / "test_download.zip"),
            name_ends_with=".zip",
        )
