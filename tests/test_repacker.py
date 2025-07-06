# SPDX-FileCopyrightText: 2025-present Erik Abair <erik.abair@bearbrains.work>
#
# SPDX-License-Identifier: MIT
import os

from python_xiso_repacker.util.extract_xiso import _download_latest_extract_xiso


def test_download_works(tmp_path):
    output_file = tmp_path / "extract-xiso"

    assert _download_latest_extract_xiso(output_file)

    assert os.path.isfile(output_file)
