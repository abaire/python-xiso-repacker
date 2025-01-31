# SPDX-FileCopyrightText: 2025-present Erik Abair <erik.abair@bearbrains.work>
#
# SPDX-License-Identifier: MIT
import os

from nxdk_pgraph_test_repacker import download_latest_iso


def test_download_works(tmp_path):
    output_file = tmp_path / "downloaded.iso"

    assert download_latest_iso(output_file)

    assert os.path.isfile(output_file)
