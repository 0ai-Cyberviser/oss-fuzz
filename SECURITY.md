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

## Known Security Constraints

### Protobuf Dependency Limitation

**Current Status**: This repository is constrained to protobuf 3.20.3 due to dependencies.

**Constraint Chain**:
```
infra/cifuzz/requirements.txt
  └── clusterfuzz==2.6.0
      └── google-cloud-datastore==1.12.0
          └── protobuf>=3.4.0,<4.0.0
```

**Known Vulnerabilities**: protobuf 3.20.3 has known CVEs that are patched in versions 4.25.8+, 5.29.6+:
- JSON recursion depth bypass (CVE affecting versions < 5.29.6)
- Denial of Service via uncontrolled recursion (CVE affecting versions < 4.25.8)

**Why Not Upgraded**:
- protobuf 4.x+ is incompatible with google-cloud-datastore 1.12.0
- clusterfuzz 2.6.0 (latest) still requires google-cloud-datastore==1.12.0
- No version path exists between 3.20.3 and 4.21.x (no 3.21.x series)

**Risk Assessment**: The vulnerabilities primarily enable DoS attacks through crafted protobuf messages. OSS-Fuzz infrastructure controls input sources, reducing exploitation risk.

**Resolution Path**: This constraint will be resolved when:
- clusterfuzz releases a version supporting google-cloud-datastore 2.x+, OR
- An alternative to the clusterfuzz dependency is implemented

**Upstream Alignment**: The upstream google/oss-fuzz repository has the same constraint. This fork maintains alignment with upstream.

*Last assessed: 2026-03-29*
