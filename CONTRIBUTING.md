# Contributing

Contributions are welcome! Here's how to get started.

## Setup

```bash
git clone https://github.com/rmoralespp/jsonl.git
cd jsonl
```

## Tests

```bash
pip install --group=test --upgrade
python -Wd -m pytest tests/ --cov
```

## Lint

```bash
pip install --group=lint --upgrade
ruff check .
```

## Docs

```bash
pip install --group=doc --upgrade
zensical build
zensical serve
```

> See [zensical docs](https://zensical.org/docs/usage/) for more details.

## Pull Requests

1. Fork the repo and create a branch from `main`.
2. Add tests for any new functionality.
3. Ensure all tests pass and linting is clean.
4. Open a PR with a clear description of the change.
