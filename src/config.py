"""This file manages all configurations of the software as single point of truth."""

from pathlib import Path
import os

ROOT_DIRECTORY: Path = os.getcwd()
DATA_DIRECTORY: Path = ROOT_DIRECTORY / Path("data")
# The supported file formats are not listed here: every reader registers itself (see readers.py)
