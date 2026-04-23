# Hancock Fuzzing Suite

This directory contains comprehensive fuzz targets for the Hancock project, built from scratch for OSS-Fuzz integration.

## Fuzz Targets

### 1. fuzz_parser.py
**Purpose**: Tests parsing functionality for multiple data formats.

**Coverage**:
- JSON parsing with malformed inputs
- YAML parsing with complex structures
- Custom text protocol parsing
- Edge cases: nested data, special characters, encoding issues

**Approach**: Uses FuzzedDataProvider to select parsing strategies and generate varied input data.

### 2. fuzz_validator.py
**Purpose**: Tests validation functions for common data types.

**Coverage**:
- Email format validation
- URL format validation
- IPv4 address validation
- Phone number validation
- Password strength checking

**Approach**: Fuzzes validation logic with malformed, edge-case, and valid inputs to find parser bugs and validation bypasses.

### 3. fuzz_processor.py
**Purpose**: Tests data encoding, decoding, hashing, and compression.

**Coverage**:
- Base64 encoding/decoding (standard and URL-safe)
- Hex encoding/decoding
- Hash algorithms (MD5, SHA1, SHA256, SHA512, BLAKE2b)
- Data compression and decompression
- Text transformations

**Approach**: Fuzzes data transformation pipelines to find crashes in encoding/decoding and compression libraries.

### 4. fuzz_api.py
**Purpose**: Tests API request/response handling.

**Coverage**:
- URL query string parsing
- URL component parsing
- Query string building
- API request parsing (JSON-based)
- API response building
- API key validation

**Approach**: Fuzzes API layer to find injection vulnerabilities, parser bugs, and validation issues.

### 5. fuzz_config.py
**Purpose**: Tests configuration file parsing and validation.

**Coverage**:
- JSON configuration parsing
- INI configuration parsing
- Configuration structure validation
- Configuration merging
- Default value application

**Approach**: Fuzzes configuration handling to find parser bugs and logic errors in config processing.

## Seed Corpus

Each fuzzer has a dedicated seed corpus in `corpus/<fuzzer_name>/` containing:
- Valid inputs representing common use cases
- Edge cases
- Examples that exercise different code paths

## Building and Testing

### Build the fuzzers:
```bash
cd /path/to/oss-fuzz
python3 infra/helper.py build_image hancock
python3 infra/helper.py build_fuzzers hancock
```

### Check the build:
```bash
python3 infra/helper.py check_build hancock
```

### Run a specific fuzzer:
```bash
python3 infra/helper.py run_fuzzer hancock fuzz_parser
```

### Generate coverage:
```bash
python3 infra/helper.py build_fuzzers --sanitizer coverage hancock
python3 infra/helper.py coverage hancock --fuzz-target=fuzz_parser
```

## Design Philosophy

These fuzzers are designed to:
1. **Be comprehensive**: Cover multiple attack surfaces and code paths
2. **Be efficient**: Use FuzzedDataProvider for structured fuzzing
3. **Be resilient**: Catch and handle expected exceptions (resource exhaustion)
4. **Be maintainable**: Clear structure, documentation, and error handling

## Enhancement Strategy

The "enhanced" fuzzing approach includes:
- **Multi-strategy fuzzing**: Each fuzzer tests multiple related functions
- **Structured input generation**: Using FuzzedDataProvider for better coverage
- **Seed corpus**: Providing good initial inputs for mutation
- **Exception handling**: Properly catching expected vs. unexpected errors
- **Resource limits**: Handling MemoryError, RecursionError, SystemError gracefully

## Future Enhancements

Potential improvements:
1. Add dictionary files for specific parsers
2. Expand seed corpus with real-world examples
3. Add more specialized fuzzers for specific Hancock modules
4. Implement custom mutators for structured data
5. Add fuzz targets for security-critical operations

## Author

Built from scratch for the 0ai-Cyberviser/Hancock project.
Copyright 2026 - Licensed under Apache 2.0
