# pre-commit-terraform-fmt [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A [pre-commit](https://pre-commit.com/) hook to rewrite Terraform configuration files to a canonical format.

## Usage

`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/melmorabity/pre-commit-terraform-fmt
  rev: 0.0.1
  hooks:
    - id: terraform-fmt
      # Optional argument: path to the Terraform executable
      # args: [--terraform=/usr/local/bin/terraform]
```
