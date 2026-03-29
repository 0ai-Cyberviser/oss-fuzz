# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it
responsibly. **Do not open a public issue.**

Please report vulnerabilities through
[GitHub Security Advisories](https://github.com/0ai-Cyberviser/oss-fuzz/security/advisories).
Click **"New draft security advisory"** and include as much detail as possible:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

## Scope

This policy applies to the infrastructure code in this repository (the `infra/`
directory, GitHub Actions workflows, and supporting tooling). Individual fuzzing
project configurations under `projects/` are maintained by their respective
upstream project owners.

## Response

We will acknowledge receipt of your report within **72 hours** and aim to
provide an initial assessment within **7 business days**. We will work with you
to understand and address the issue before any public disclosure.

## Supported Versions

Only the latest version of the code on the default branch is actively
maintained and receives security updates.

## Known Dependency Vulnerabilities

### protobuf 3.20.2 (Accepted Risk)

The `protobuf` package is pinned to version 3.20.2 in
`infra/build/functions/requirements.txt` and `infra/cifuzz/requirements.txt`.
This version has known vulnerabilities:

- **JSON recursion depth bypass** (patched in 5.29.6+)
- **Potential Denial of Service** (patched in 4.25.8+)

**Why it cannot be upgraded:** The `google-cloud-datastore<2.0` and
`google-cloud-ndb==1.7.1` packages ship pre-compiled protobuf descriptor files
(`_pb2.py`) generated with protobuf 3.x. These descriptors are incompatible
with the protobuf 4.x+ runtime, which raises `TypeError: Descriptors cannot be
created directly` at import time. The `clusterfuzz==2.5.9` package further pins
`google-cloud-datastore==1.12.0`, reinforcing this constraint.

Upgrading protobuf requires simultaneously upgrading the entire Google Cloud
dependency stack (`google-cloud-datastore>=2.0`, `google-cloud-ndb>=2.0`,
`google-cloud-scheduler>=2.0`, `google-api-core>=2.0`) and updating all
call sites to the new APIs. This is tracked as a future improvement.

**Mitigation:** This infrastructure code runs in controlled server-side
environments, not exposed to untrusted protobuf input. The upstream
[google/oss-fuzz](https://github.com/google/oss-fuzz) repository uses the same
pinned version.
