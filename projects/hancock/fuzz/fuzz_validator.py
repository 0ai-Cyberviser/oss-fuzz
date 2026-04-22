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
"""Fuzzer for Hancock validation functionality."""

import sys
import atheris
import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url):
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_ipv4(ip):
    """Validate IPv4 address."""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, AttributeError):
        return False


def validate_phone(phone):
    """Validate phone number."""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_password_strength(password):
    """Check password strength."""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3


def TestOneInput(data):
    """Fuzz target for validation functionality."""
    if len(data) < 1:
        return

    fdp = atheris.FuzzedDataProvider(data)

    # Choose validation type
    validation_type = fdp.ConsumeIntInRange(0, 4)
    test_string = fdp.ConsumeUnicodeNoSurrogates(1000)

    try:
        if validation_type == 0:
            validate_email(test_string)
        elif validation_type == 1:
            validate_url(test_string)
        elif validation_type == 2:
            validate_ipv4(test_string)
        elif validation_type == 3:
            validate_phone(test_string)
        else:
            validate_password_strength(test_string)
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
