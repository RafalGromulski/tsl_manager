from configparser import ConfigParser, MissingSectionHeaderError
from typing import Dict


def load_config(filename: str = "config/database.ini", section: str = "postgresql") -> Dict[str, str]:
    parser = ConfigParser()
    try:
        parser.read(filename)
    except MissingSectionHeaderError:
        raise ValueError(f"Invalid INI format: missing section headers in '{filename}'.")

    if not parser.has_section(section):
        raise ValueError(f"Section '{section}' not found in the '{filename}' file.")

    return {key: value for key, value in parser.items(section)}
