# Security Policy

## Overview

OSS-Fuzz is a continuous fuzzing service for open source software. Security is
central to the project's mission—we help find and fix vulnerabilities in open
source projects. We take the security of this infrastructure seriously.

## Supported Versions

This repository tracks the latest development of the OSS-Fuzz platform. We
support only the latest version on the `main` branch. There are no separately
maintained release branches.

| Branch   | Supported          |
| -------- | ------------------ |
| `main`   | :white_check_mark: |
| Others   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in the OSS-Fuzz infrastructure (build
scripts, CI configuration, container definitions, or supporting code in this
repository), please report it responsibly.

### How to Report

1. **Do not open a public issue.** Security vulnerabilities should be reported
   privately so that they can be addressed before public disclosure.
2. **Use GitHub Private Vulnerability Reporting.** Navigate to the
   [Security Advisories](https://github.com/0ai-Cyberviser/oss-fuzz/security/advisories)
   page and click **"Report a vulnerability"** to submit a private report.
3. **Alternatively, contact via email.** You may email
   [oss-fuzz-team@google.com](mailto:oss-fuzz-team@google.com) with details of
   the vulnerability.

### What to Include

- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue, or a proof-of-concept if available.
- The affected files or components (e.g., project build scripts, infrastructure
  code, CI workflows).
- Any suggested mitigations or fixes.

### What to Expect

- **Acknowledgment:** We aim to acknowledge receipt of your report within
  **3 business days**.
- **Assessment:** We will evaluate the report and provide an initial assessment
  within **10 business days**.
- **Resolution:** Confirmed vulnerabilities will be addressed as quickly as
  possible. We will coordinate with you on an appropriate disclosure timeline.
- **Credit:** We appreciate responsible disclosure and are happy to credit
  reporters in any related advisory, unless you prefer to remain anonymous.

## Scope

This policy covers vulnerabilities in the OSS-Fuzz infrastructure itself,
including:

- Build and CI configuration files
- Docker container definitions
- Python infrastructure code (`infra/`)
- Project integration scripts (`projects/`)

For vulnerabilities found **in fuzzed open source projects** (i.e., bugs
discovered by OSS-Fuzz), please refer to the
[OSS-Fuzz documentation](https://google.github.io/oss-fuzz/) on disclosure
policies and report them to the respective upstream project maintainers.
