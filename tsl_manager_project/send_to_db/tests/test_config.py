import pytest
from tempfile import NamedTemporaryFile
from send_to_db.config import load_config


@pytest.fixture
def valid_ini_file():
    with NamedTemporaryFile(mode="w+", suffix=".ini", delete=False) as temp:
        temp.write(
            "[postgresql]\n"
            "host=localhost\n"
            "database=test_db\n"
            "user=test_user\n"
            "password=secret\n"
            "port=5433\n"
        )
        temp.flush()
        yield temp.name


def test_load_config_valid(valid_ini_file):
    config = load_config(valid_ini_file, "postgresql")
    assert config["host"] == "localhost"
    assert config["database"] == "test_db"
    assert config["user"] == "test_user"
    assert config["password"] == "secret"
    assert config["port"] == "5433"


def test_missing_section(valid_ini_file):
    with pytest.raises(ValueError, match="Section 'mysql' not found"):
        load_config(valid_ini_file, "mysql")


def test_empty_ini_file():
    with NamedTemporaryFile(mode="w+", suffix=".ini", delete=False) as temp:
        temp.write("")
        temp.flush()
        filename = temp.name

    with pytest.raises(ValueError, match="Section 'postgresql' not found"):
        load_config(filename, "postgresql")


def test_malformed_ini_file():
    with NamedTemporaryFile(mode="w+", suffix=".ini", delete=False) as temp:
        temp.write("not a valid ini structure")
        temp.flush()
        filename = temp.name

    with pytest.raises(ValueError, match="missing section headers"):
        load_config(filename, "postgresql")
