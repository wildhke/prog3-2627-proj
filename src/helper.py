"""This module holds all required helper functions to run the app."""

from .config import DATA_DIRECTORY

def get_files_in_directory(file_format: str) -> list[str]:
    return DATA_DIRECTORY.glob("*" + file_format)