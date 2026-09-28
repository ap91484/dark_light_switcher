# Dark/Light Switcher

A small Python utility for Ubuntu 24.04 that automatically switches GNOME's
color scheme according to sunrise and sunset at your location. It uses
[`suntime`](https://pypi.org/project/suntime/) to calculate sun times.

The app applies `prefer-light` between sunrise and sunset, and `prefer-dark`
otherwise. It checks immediately when started and then every five minutes, so
changes can occur up to five minutes after sunrise or sunset. Applications that
respect GNOME's color-scheme preference follow the change.

## Requirements

- Ubuntu with a GNOME desktop (the project's target is Ubuntu 24.04).
- Python 3.10 or newer, with `pip` and virtual environment support.
- `gsettings`, available in your logged-in desktop session.
- A systemd user session for the optional background service.

## Installation

From the project directory:

```bash
python3 -m venv venv
venv/bin/python -m pip install .
```

If virtual environment support is missing on Ubuntu, install it first:

```bash
sudo apt install python3-venv
```

## Make targets

With the existing `venv` in place, run `make all` to install the executable,
link it into `~/.local/bin`, copy the service, and enable/start it.

| Target | Action |
| --- | --- |
| `make executable` | Install with pip in `venv` and link into `~/.local/bin`. |
| `make service` | Copy the unit into `~/.config/systemd/user/`. |
| `make start` | Build both prerequisites, reload systemd, and enable/start it. |
| `make all` | Run `make start` (also the default target). |

The Makefile copies the service into `~/.config/systemd/user/`, where systemd
finds user units automatically.
The supplied unit's executable path works with the link created by
`make executable`. Edit the coordinates in the project service file before
running `make all`. If the service is already running when you change its
configuration, run `systemctl --user restart ubuntu-theme-switcher.service`
after `make all` to apply it.

You can override paths, for example `make all VENV=/absolute/path/to/venv`.
`BIN_DIR` and `SERVICE_DIR` are also configurable; if you override `BIN_DIR`,
update the service's `ExecStart=` accordingly.

## Usage

Run from a terminal in your desktop session:

```bash
venv/bin/dark-light-switcher
```

The process keeps running until you stop it with `Ctrl+C`. Stopping it leaves
the current color-scheme preference in place.

Set your location using environment variables:

```bash
LOCATION_LATITUDE=52.5200 LOCATION_LONGITUDE=13.4050 venv/bin/dark-light-switcher
```

Coordinates are decimal degrees: north and east are positive; south and west
are negative.

| Variable | Default |
| --- | --- |
| `LOCATION_LATITUDE` | `49.7333` |
| `LOCATION_LONGITUDE` | `11.1500` |

If either variable cannot be converted to a number, the app reports the error
and uses both default coordinates. The check interval is defined by
`CHECK_INTERVAL_SECONDS` in [`main.py`](src/dark_light_switcher/main.py);
it is not configurable through an environment variable.

## Run automatically with systemd

The included [`ubuntu-theme-switcher.service`](ubuntu-theme-switcher.service)
is a **user service** tied to the graphical session.

1. Copy it to your user service directory:

   ```bash
   mkdir -p ~/.config/systemd/user
   cp ubuntu-theme-switcher.service ~/.config/systemd/user/
   ```

2. Edit `~/.config/systemd/user/ubuntu-theme-switcher.service`. Set the two
   `Environment=` lines to your coordinates and update `ExecStart=` to the
   absolute path of the executable installed above, for example:

   ```ini
   Environment="LOCATION_LATITUDE=52.5200"
   Environment="LOCATION_LONGITUDE=13.4050"
   ExecStart=/home/your-user/dark_light_switcher/venv/bin/dark-light-switcher
   ```

   The supplied service uses `%h/.local/bin/dark-light-switcher`. If you ran
   `make executable`, its symlink already provides this path and you can keep
   it. For a manual virtual environment installation, use the absolute path
   shown above, replacing it with your actual project location.

3. Reload systemd and enable the service for future graphical sessions,
   starting it now as well:

   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now ubuntu-theme-switcher.service
   ```

Inspect status and logs:

```bash
systemctl --user status ubuntu-theme-switcher.service
journalctl --user -u ubuntu-theme-switcher.service -f
```

After editing the service configuration, apply it with:

```bash
systemctl --user daemon-reload
systemctl --user restart ubuntu-theme-switcher.service
```

To stop the service and disable automatic startup:

```bash
systemctl --user disable --now ubuntu-theme-switcher.service
```

## Troubleshooting

- **The service cannot start:** check that `ExecStart=` points to the installed
  executable and that the virtual environment still exists.
- **The theme does not change:** run the app as your desktop user in the
  graphical session. Check the current preference with
  `gsettings get org.gnome.desktop.interface color-scheme`. Applications that
  do not honor this preference may need their own theme settings.
- **Sun-time calculation errors:** check your coordinates and the service
  logs. If sunrise or sunset cannot be calculated, such as during polar day
  or night, the app logs the error, leaves the preference unchanged, and
  retries after five minutes.
