import configparser
from types import SimpleNamespace
from unittest.mock import patch

from fanctrl.controller import get_cpu_temp, get_system_load, load_config


def test_load_config_creates_file(tmp_path):
    cfg_path = tmp_path / "fanctrl.conf"
    config = load_config(str(cfg_path))
    assert cfg_path.exists()
    assert config["fan"]["gpio"] == "18"


@patch("psutil.sensors_temperatures")
def test_get_cpu_temp(mock_temps):
    mock_temps.return_value = {"cpu-thermal": [SimpleNamespace(current=42.0)]}
    assert get_cpu_temp() == 42.0


@patch("os.getloadavg")
def test_get_system_load(mock_load):
    mock_load.return_value = (1.2345, 0.5, 0.25)
    assert get_system_load() == ("1.23", "0.50", "0.25")
