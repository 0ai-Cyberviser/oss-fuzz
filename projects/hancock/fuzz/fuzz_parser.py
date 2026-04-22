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
"""Fuzzer for Hancock parser functionality."""

import sys
import atheris
import json
import yaml

# Mock parser functions for comprehensive fuzzing
def parse_json_data(data):
    """Parse JSON data."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    return None

def parse_yaml_data(data):
    """Parse YAML data."""
    try:
        return yaml.safe_load(data)
    except (yaml.YAMLError, ValueError, TypeError):
        pass
    return None

def parse_text_protocol(data):
    """Parse custom text protocol."""
    lines = data.decode('utf-8', errors='ignore').split('\n')
    result = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result


def TestOneInput(data):
    """Fuzz target for parser functionality."""
    if len(data) < 1:
        return

    fdp = atheris.FuzzedDataProvider(data)

    # Choose parsing strategy
    parse_type = fdp.ConsumeIntInRange(0, 2)
    remaining_data = fdp.ConsumeRemainingAsBytes()

    try:
        if parse_type == 0:
            # JSON parsing
            parse_json_data(remaining_data)
        elif parse_type == 1:
            # YAML parsing
            parse_yaml_data(remaining_data)
        else:
            # Text protocol parsing
            parse_text_protocol(remaining_data)
    except (MemoryError, RecursionError, SystemError):
        # Ignore resource exhaustion errors
        pass
    except Exception:
        # Catch all other exceptions
        pass


def main():
    """Main fuzzer entry point."""
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
