# SPDX-FileCopyrightText: 2025-present Erik Abair <erik.abair@bearbrains.work>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING

from python_xiso_repacker.util.extract_xiso import ensure_extract_xiso

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)

__all__ = ["ensure_extract_xiso", "extract_file", "replace_file", "run"]


def _copy_file(src: str, dst: str) -> None:
    """Copies src to dst, creating any necessary parent directories."""
    dst_dir = os.path.dirname(dst)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)
    shutil.copy(src, dst)


def _ensure_output_directory(output: str) -> str:
    if os.path.isdir(output) or not output.endswith(".iso"):
        output = os.path.join(output, "xiso-updated.iso")

    dst_dir = os.path.dirname(output)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)

    return output


def replace_file(
    iso_file: str, output_file: str, target_file: str, replacement_file: str, extract_xiso_binary: str
) -> bool:
    """Updates the given xiso by replacing target_file with replacement_file."""
    logger.info("Repacking file %s::%s from %s using %s", iso_file, target_file, replacement_file, extract_xiso_binary)

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.run([extract_xiso_binary, "-d", tmpdir, "-x", iso_file], capture_output=True, check=True)
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Failed to extract iso %s using %s", iso_file, extract_xiso_binary)
            return False

        target_path = os.path.join(tmpdir, target_file)
        _copy_file(replacement_file, target_path)

        try:
            subprocess.run([extract_xiso_binary, "-c", tmpdir, output_file], capture_output=True, check=True)
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Failed to create iso %s using %s", output_file, extract_xiso_binary)
            return False
        logger.info("Generated %s", output_file)

    return True


def extract_file(iso_file: str, target_file: str, output_file: str, extract_xiso_binary: str) -> bool:
    """Extracts target_file from the given iso_file and writes it to the given location."""
    logger.info("Extracting %s from %s using %s", target_file, iso_file, extract_xiso_binary)

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.run([extract_xiso_binary, "-d", tmpdir, "-x", iso_file], capture_output=True, check=True)
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Failed to extract iso %s using %s", iso_file, extract_xiso_binary)
            return False

        extracted_file_path = os.path.join(tmpdir, target_file)
        if not os.path.isfile(extracted_file_path):
            logger.error("Target file %s not found in %s", target_file, iso_file)
            return False

        logger.info("Retrieved %s", os.path.basename(extracted_file_path))
        _copy_file(extracted_file_path, output_file)
        return True


def run(argv: Sequence[str] | None = None):
    """Parses program arguments and executes the repacker."""

    parser = argparse.ArgumentParser(description="Tool to replace or extract files within Xbox ISO (xiso) images.")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enables verbose logging information",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Path to where the reconfigured xiso should be saved (default: xiso-updated.iso)",
        default="xiso-updated.iso",
    )
    parser.add_argument("--extract-xiso-tool", "-T", help="Path to the extract-xiso tool")
    parser.add_argument("iso", metavar="path_to_iso", help="Path to the xiso file to read/reconfigure")

    parser.add_argument("target_file", help="Path to the file within the ISO to extract or replace")

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--replace", "-r", metavar="replacement_file", help="Path to file that will replace the target file in the ISO"
    )
    action.add_argument(
        "--extract",
        "-e",
        metavar="extracted_filepath",
        help="Extract the target file from the xiso and copy it to the given destination path",
    )

    args = parser.parse_args(argv)

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    iso_file = args.iso
    if not os.path.isfile(iso_file):
        logger.error("Input ISO '%s' not found!", iso_file)
        sys.exit(2)

    if args.replace and not os.path.isfile(args.replace):
        logger.error("Replacement file '%s' not found!", args.replace)
        sys.exit(2)

    extract_xiso = ensure_extract_xiso(args.extract_xiso_tool)
    if not extract_xiso:
        logger.error("extract-xiso tool not found")
        sys.exit(3)

    if args.replace and not replace_file(
        iso_file, _ensure_output_directory(args.output), args.target_file, args.replace, extract_xiso
    ):
        sys.exit(100)

    if args.extract and not extract_file(iso_file, args.target_file, args.extract, extract_xiso):
        sys.exit(100)

    sys.exit(0)
