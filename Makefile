.DEFAULT_GOAL := all

VENV ?= $(CURDIR)/venv
BIN_DIR ?= $(HOME)/.local/bin
SERVICE_DIR ?= $(HOME)/.config/systemd/user
SERVICE_NAME := ubuntu-theme-switcher.service
EXECUTABLE := dark-light-switcher
PYTHON := $(VENV)/bin/python
VENV_EXECUTABLE := $(VENV)/bin/$(EXECUTABLE)
INSTALLED_EXECUTABLE := $(BIN_DIR)/$(EXECUTABLE)
INSTALLED_SERVICE := $(SERVICE_DIR)/$(SERVICE_NAME)
PROJECT_FILES := pyproject.toml README.md $(wildcard src/dark_light_switcher/*.py)

.PHONY: all executable service start check-venv

all: start

# Use the existing virtual environment; do not create a new one.
check-venv:
	@test -x "$(PYTHON)" || { echo "Missing virtual environment Python: $(PYTHON)" >&2; exit 1; }
	@"$(PYTHON)" -m pip --version >/dev/null

executable: $(INSTALLED_EXECUTABLE)

$(VENV_EXECUTABLE): $(PROJECT_FILES) | check-venv
	"$(PYTHON)" -m pip install .

$(INSTALLED_EXECUTABLE): $(VENV_EXECUTABLE) | $(BIN_DIR)
	ln -sfn "$(abspath $(VENV_EXECUTABLE))" "$@"

$(BIN_DIR) $(SERVICE_DIR):
	mkdir -p "$@"

service: $(INSTALLED_SERVICE)

$(INSTALLED_SERVICE): $(SERVICE_NAME) | $(SERVICE_DIR)
	cp "$<" "$@"

# Reload unit files before enabling and starting the service.
start: executable service
	systemctl --user daemon-reload
	systemctl --user enable --now "$(SERVICE_NAME)"
