#!/usr/bin/python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Fuzzer for Hancock configuration parsing and validation."""

import sys
import atheris
import json
import configparser
from io import StringIO


def parse_json_config(data):
    """Parse JSON configuration."""
    return json.loads(data)


def parse_ini_config(data):
    """Parse INI configuration."""
    config = configparser.ConfigParser()
    config.read_string(data)
    result = {}
    for section in config.sections():
        result[section] = dict(config.items(section))
    return result


def validate_config_structure(config):
    """Validate configuration structure."""
    if not isinstance(config, dict):
        return False

    # Check for required fields
    required_fields = ['version', 'settings']
    for field in required_fields:
        if field not in config:
            return False

    # Validate types
    if not isinstance(config.get('version'), (str, int, float)):
        return False
    if not isinstance(config.get('settings'), dict):
        return False

    return True


def merge_configs(config1, config2):
    """Merge two configurations."""
    if not isinstance(config1, dict) or not isinstance(config2, dict):
        return config1

    result = config1.copy()
    for key, value in config2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def apply_config_defaults(config, defaults):
    """Apply default values to configuration."""
    if not isinstance(defaults, dict):
        return config

    result = defaults.copy()
    if isinstance(config, dict):
        result.update(config)
    return result


def TestOneInput(data):
    """Fuzz target for configuration functionality."""
    if len(data) < 1:
        return

    fdp = atheris.FuzzedDataProvider(data)

    # Choose config operation
    operation = fdp.ConsumeIntInRange(0, 4)

    try:
        if operation == 0:
            # Parse JSON config
            config_data = fdp.ConsumeRemainingAsString()
            parsed = parse_json_config(config_data)
            validate_config_structure(parsed)
        elif operation == 1:
            # Parse INI config
            config_data = fdp.ConsumeRemainingAsString()
            parse_ini_config(config_data)
        elif operation == 2:
            # Validate config structure
            config_data = fdp.ConsumeRemainingAsString()
            try:
                config = json.loads(config_data)
                validate_config_structure(config)
            except json.JSONDecodeError:
                pass
        elif operation == 3:
            # Merge configs
            size1 = fdp.ConsumeIntInRange(1, 100)
            size2 = fdp.ConsumeIntInRange(1, 100)
            config1_str = fdp.ConsumeUnicodeNoSurrogates(size1)
            config2_str = fdp.ConsumeUnicodeNoSurrogates(size2)
            try:
                config1 = json.loads(config1_str)
                config2 = json.loads(config2_str)
                merge_configs(config1, config2)
            except json.JSONDecodeError:
                pass
        else:
            # Apply defaults
            size1 = fdp.ConsumeIntInRange(1, 100)
            config_str = fdp.ConsumeUnicodeNoSurrogates(size1)
            defaults_str = fdp.ConsumeRemainingAsString()
            try:
                config = json.loads(config_str)
                defaults = json.loads(defaults_str)
                apply_config_defaults(config, defaults)
            except json.JSONDecodeError:
                pass
    except (MemoryError, RecursionError, SystemError):
        pass
    except Exception:
        pass


def main():
    """Main fuzzer entry point."""
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
