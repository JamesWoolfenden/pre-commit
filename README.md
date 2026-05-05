# pre-commit

[![Build Status](https://github.com/JamesWoolfenden/pre-commit/workflows/Verify%20and%20Bump/badge.svg?branch=master)](https://github.com/JamesWoolfenden/pre-commit)
[![Latest Release](https://img.shields.io/github/release/JamesWoolfenden/pre-commit.svg)](https://github.com/JamesWoolfenden/pre-commit/releases/latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

After <https://github.com/melmorabity/pre-commit-terraform-fmt>

## Terraform-fmt / Tofu-fmt

A [pre-commit](https://pre-commit.com/) hook to rewrite Terraform / OpenTofu configuration files to a canonical format.

The hook auto-detects the binary: it prefers `tofu` (OpenTofu) if found on `PATH`, otherwise falls back to `terraform`. Matches `.tf`, `.tfvars`, `.tofu` and `.tofuvars` files. Use `tofu-fmt` or `terraform-fmt` as the hook id — both run the same implementation.

`.pre-commit-config.yaml`:

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.1
  hooks:
    - id: tofu-fmt
      # Optional: pin a specific binary
      # args: [--terraform=/usr/local/bin/tofu]
```

## Checkov-scan

This runs the Static analysis tool https://www.checkov.io/ for Terraform, the hook automatically installs the Checkov tool.

For Checkov-scan:

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.18
  hooks:
    - id: checkov-scan
      files: \.tf$
```

## tf2docs

Updates README.md with Terraform parameters, modules.
Requires:
```
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
```
The Hook will update in-betweeen with the Terraform-Docs created content.
The hook requires that [terraform-docs](https://github.com/segmentio/terraform-docs) be installed, then add a section to you pre-commit-config.yml, updating to the latest version :

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.22
  hooks:
    - id: tf2docs
```

### Contributors
[![James Woolfenden][jameswoolfenden_avatar]][jameswoolfenden_homepage]<br/>[James Woolfenden][jameswoolfenden_homepage]<br/>
[![asottile][asottile_avatar]][asottile_homepage]<br/>[asottitle][asottile_homepage]<br/>

[asottile_homepage]: https://github.com/asottile
[asottile_avatar]: https://github.com/asottile.png?size=150
[jameswoolfenden_homepage]: https://github.com/jameswoolfenden
[jameswoolfenden_avatar]: https://github.com/jameswoolfenden.png?size=150
