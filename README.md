# FanCtrl

FanCtrl controls a GPIO-connected fan on a Raspberry Pi based on the CPU temperature.
The project uses the `logging` module and obtains system metrics through `psutil`
and standard operating system functions. A sample configuration file is provided as
`fanctrl.conf` and can be placed elsewhere via the `--config` option (default:
`/etc/fanctrl/fanctrl.conf`).

## Development

The Python code resides in the `fanctrl` package under `src/`. Tests live in the
`tests/` directory and can be executed with `pytest`:

```bash
PYTHONPATH=src pytest
```

## Debian Package

A minimal Debian packaging setup is available for installation via `apt-get`. The
required metadata is located in the `debian/` directory and can be processed with
standard Debian tools.

