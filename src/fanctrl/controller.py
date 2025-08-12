"""Core fan control logic."""
from __future__ import annotations

import argparse
import configparser
import logging
import os
import time
from typing import Tuple

try:
    import RPi.GPIO as GPIO
except Exception:  # pragma: no cover - hardware dependent
    class _MockGPIO:
        BCM = OUT = HIGH = LOW = None
        def setmode(self, mode):
            raise RuntimeError("GPIO not available")
        def setwarnings(self, flag):
            pass
        def setup(self, gpio, mode):
            pass
        def input(self, gpio):
            return False
        def output(self, gpio, state):
            pass
    GPIO = _MockGPIO()

import psutil

DEFAULT_CONFIG_PATH = "/etc/fanctrl/fanctrl.conf"


def load_config(path: str) -> configparser.ConfigParser:
    """Load configuration from *path*, creating defaults if missing."""
    config = configparser.ConfigParser()
    if not os.path.isfile(path):
        config["logging"] = {"level": "INFO"}
        config["fan"] = {
            "temphigh": "50.0",
            "templow": "45.0",
            "interval": "5",
            "gpio": "18",
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            config.write(fh)
    else:
        config.read(path)
    return config


def get_cpu_temp() -> float:
    """Return CPU temperature in Celsius using psutil."""
    temps = psutil.sensors_temperatures()
    for key in ("cpu-thermal", "coretemp", "k10temp"):
        entries = temps.get(key)
        if entries:
            return float(entries[0].current)
    raise RuntimeError("No CPU temperature sensor found")


def get_system_load() -> Tuple[str, str, str]:
    """Return 1, 5 and 15 minute system loads formatted as strings."""
    load1, load5, load15 = os.getloadavg()
    return tuple(f"{v:.2f}" for v in (load1, load5, load15))


class FanController:
    """Control a fan connected to a GPIO pin."""

    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.logger = logging.getLogger("fanctrl")

    def setup_gpio(self) -> int:  # pragma: no cover - hardware dependent
        gpio = int(self.config["fan"]["gpio"])
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio, GPIO.OUT)
        return gpio

    def get_state(self, gpio: int) -> bool:  # pragma: no cover - hardware dependent
        return bool(GPIO.input(gpio))

    def switch_fan(self, gpio: int, state: bool) -> bool:  # pragma: no cover - hardware dependent
        old_state = self.get_state(gpio)
        if state and not old_state:
            GPIO.output(gpio, GPIO.HIGH)
            return True
        if not state and old_state:
            GPIO.output(gpio, GPIO.LOW)
            return True
        return False

    def run(self) -> None:
        """Start monitoring CPU temperature and toggle fan accordingly."""
        gpio = self.setup_gpio()
        temp_high = float(self.config["fan"]["temphigh"])
        temp_low = float(self.config["fan"]["templow"])
        interval = int(self.config["fan"]["interval"])
        self.logger.info(
            "Starting fan monitoring (high=%s°C low=%s°C)", temp_high, temp_low
        )
        try:
            while True:
                temp = get_cpu_temp()
                loads = get_system_load()
                self.logger.debug(
                    "Temperature: %s°C Load: %s/%s/%s", temp, *loads
                )
                if temp >= temp_high:
                    if self.switch_fan(gpio, True):
                        self.logger.info(
                            "Fan switched on at %s°C", temp
                        )
                elif temp < temp_low:
                    if self.switch_fan(gpio, False):
                        self.logger.info(
                            "Fan switched off at %s°C", temp
                        )
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Terminated by user")
        finally:
            self.switch_fan(gpio, True)
            self.logger.info("Fan left running")


def main() -> None:
    parser = argparse.ArgumentParser(description="Raspberry Pi fan controller")
    parser.add_argument(
        "--config", "-c", default=DEFAULT_CONFIG_PATH, help="Path to configuration file"
    )
    args = parser.parse_args()
    config = load_config(args.config)
    logging.basicConfig(
        level=getattr(logging, config["logging"].get("level", "INFO"))
    )
    controller = FanController(config)
    controller.run()


if __name__ == "__main__":  # pragma: no cover
    main()
