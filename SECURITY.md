# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

If you discover a security issue (e.g., secret leakage, dependency vulnerability, XSS in Streamlit components), please report it privately via the **GitHub Security Advisories** tab on this repository.

We aim to acknowledge receipt within 48 hours and will work with you to assess and resolve the issue promptly.

## Security Measures in Place

- **Dependency Scanning**: Automated via GitHub Actions (`pip-audit`) on every push
- **Secret Detection**: `gitleaks` runs in CI to prevent API key commits
- **Input Sanitization**: Country search inputs are sanitized to prevent injection
- **Public Data Only**: No sensitive user data is collected or stored
