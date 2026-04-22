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
"""Fuzzer for Hancock API functionality."""

import sys
import atheris
import json
from urllib.parse import parse_qs, urlparse, urlencode


def parse_query_string(query):
    """Parse URL query string."""
    return parse_qs(query)


def parse_url(url):
    """Parse URL into components."""
    return urlparse(url)


def build_query_string(params):
    """Build query string from parameters."""
    return urlencode(params)


def parse_api_request(data):
    """Parse API request data."""
    try:
        request = json.loads(data)
        # Validate required fields
        if not isinstance(request, dict):
            return None

        method = request.get('method', 'GET')
        path = request.get('path', '/')
        headers = request.get('headers', {})
        body = request.get('body', '')

        return {
            'method': method,
            'path': path,
            'headers': headers,
            'body': body
        }
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def build_api_response(status_code, data, headers=None):
    """Build API response."""
    response = {
        'status': status_code,
        'data': data,
        'headers': headers or {}
    }
    return json.dumps(response)


def validate_api_key(api_key):
    """Validate API key format."""
    if not api_key or len(api_key) < 16:
        return False
    # Check for valid characters
    return all(c.isalnum() or c in '-_' for c in api_key)


def TestOneInput(data):
    """Fuzz target for API functionality."""
    if len(data) < 1:
        return

    fdp = atheris.FuzzedDataProvider(data)

    # Choose API operation
    operation = fdp.ConsumeIntInRange(0, 5)

    try:
        if operation == 0:
            # Parse query string
            query = fdp.ConsumeUnicodeNoSurrogates(500)
            parse_query_string(query)
        elif operation == 1:
            # Parse URL
            url = fdp.ConsumeUnicodeNoSurrogates(500)
            parse_url(url)
        elif operation == 2:
            # Build query string
            num_params = fdp.ConsumeIntInRange(0, 10)
            params = {}
            for _ in range(num_params):
                key = fdp.ConsumeUnicodeNoSurrogates(50)
                value = fdp.ConsumeUnicodeNoSurrogates(50)
                params[key] = value
            build_query_string(params)
        elif operation == 3:
            # Parse API request
            request_data = fdp.ConsumeRemainingAsString()
            parse_api_request(request_data)
        elif operation == 4:
            # Build API response
            status_code = fdp.ConsumeIntInRange(100, 599)
            response_data = fdp.ConsumeUnicodeNoSurrogates(500)
            build_api_response(status_code, response_data)
        else:
            # Validate API key
            api_key = fdp.ConsumeRemainingAsString()
            validate_api_key(api_key)
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
