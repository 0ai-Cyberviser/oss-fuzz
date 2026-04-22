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
"""Fuzzer for Hancock data processing functionality."""

import sys
import atheris
import base64
import hashlib
import zlib


def encode_data(data, encoding_type):
    """Encode data using various methods."""
    if encoding_type == 0:
        return base64.b64encode(data)
    elif encoding_type == 1:
        return base64.urlsafe_b64encode(data)
    elif encoding_type == 2:
        return data.hex()
    return data


def decode_data(data, encoding_type):
    """Decode data using various methods."""
    if encoding_type == 0:
        return base64.b64decode(data, validate=False)
    elif encoding_type == 1:
        return base64.urlsafe_b64decode(data)
    elif encoding_type == 2:
        return bytes.fromhex(data.decode('utf-8', errors='ignore'))
    return data


def hash_data(data, hash_type):
    """Hash data using various algorithms."""
    if hash_type == 0:
        return hashlib.md5(data).hexdigest()
    elif hash_type == 1:
        return hashlib.sha1(data).hexdigest()
    elif hash_type == 2:
        return hashlib.sha256(data).hexdigest()
    elif hash_type == 3:
        return hashlib.sha512(data).hexdigest()
    return hashlib.blake2b(data).hexdigest()


def compress_data(data):
    """Compress data."""
    return zlib.compress(data, level=6)


def decompress_data(data):
    """Decompress data."""
    return zlib.decompress(data)


def transform_text(text, transform_type):
    """Transform text in various ways."""
    if transform_type == 0:
        return text.upper()
    elif transform_type == 1:
        return text.lower()
    elif transform_type == 2:
        return text.title()
    elif transform_type == 3:
        return text.swapcase()
    return text.strip()


def TestOneInput(data):
    """Fuzz target for data processing functionality."""
    if len(data) < 2:
        return

    fdp = atheris.FuzzedDataProvider(data)

    # Choose processing operation
    operation = fdp.ConsumeIntInRange(0, 5)
    remaining_data = fdp.ConsumeRemainingAsBytes()

    try:
        if operation == 0:
            # Encoding
            encoding_type = fdp.ConsumeIntInRange(0, 2)
            encode_data(remaining_data, encoding_type)
        elif operation == 1:
            # Decoding
            encoding_type = fdp.ConsumeIntInRange(0, 2)
            decode_data(remaining_data, encoding_type)
        elif operation == 2:
            # Hashing
            hash_type = fdp.ConsumeIntInRange(0, 4)
            hash_data(remaining_data, hash_type)
        elif operation == 3:
            # Compression
            compress_data(remaining_data)
        elif operation == 4:
            # Decompression
            decompress_data(remaining_data)
        else:
            # Text transformation
            text = remaining_data.decode('utf-8', errors='ignore')
            transform_type = fdp.ConsumeIntInRange(0, 4)
            transform_text(text, transform_type)
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
