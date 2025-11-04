from configparser import ConfigParser, MissingSectionHeaderError, ParsingError


def load_config(filename: str = "config/database.ini", section: str = "postgresql") -> dict[str, str]:
    """
    Load configuration parameters from an INI file.

    Args:
        filename (str): Path to the INI configuration file. Defaults to "config/database.ini".
        section (str): Section of the configuration file to read. Defaults to "postgresql".

    Returns:
        dict[str, str]: A dictionary containing the key-value pairs from the specified section.

    Raises:
        ValueError: If the configuration file is missing section headers or the specified section is not found.
    """
    parser = ConfigParser()
    try:
        with open(filename, encoding="utf-8") as f:
            parser.read_file(f)
    except FileNotFoundError as e:
        raise ValueError(f"Config file not found: '{filename}'.") from e
    except MissingSectionHeaderError as e:
        raise ValueError(f"Invalid INI format: missing section headers in '{filename}'.") from e
    except ParsingError as e:
        raise ValueError(f"Failed to parse '{filename}': {e}") from e

    if not parser.has_section(section):
        raise ValueError(f"Section '{section}' not found in the '{filename}' file.")

    return dict(parser.items(section))
