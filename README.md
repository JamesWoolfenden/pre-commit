# pre-commit-terraform-fmt [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

After <https://github.com/melmorabity/pre-commit-terraform-fmt>

## Terraform-fmt

A [pre-commit](https://pre-commit.com/) hook to rewrite Terraform configuration files to a canonical format.

`.pre-commit-config.yaml`:

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.1
  hooks:
    - id: terraform-fmt
      # Optional argument: path to the Terraform executable
      # args: [--terraform=/usr/local/bin/terraform]
```

## Checkov-scan

This runs the Static analysis tool https://www.checkov.io/

For Checkov-scan:

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.18
  hooks:
    - id: checkov-scan
      files: \.tf$
```

## Terraform-docs

Updates README.md with parameters, modules.

```yaml
- repo: git://github.com/jameswoolfenden/pre-commit
  rev: 0.0.22
  hooks:
    - id: terraform-docs
```
