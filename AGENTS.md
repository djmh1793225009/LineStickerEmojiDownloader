# AGENTS.md

## Quick start

```bash
uv sync          # install deps from uv.lock
python src/main.py  # interactive CLI with 3 modes
```

Requires Python 3.13+ (`.python-version`, `pyproject.toml`).

## Architecture

Single entrypoint: `src/main.py` (~230 lines). No packages, no tests, no CI, no lint/typecheck config.

Pure CLI script — no web framework, no async, no config files. Downloads zip bundles from LINE CDN and strips `key` files from them.

## Key facts

- **Package manager**: `uv`. Lockfile is `uv.lock`. Do not use `pip` alone; always `uv sync` or `uv add`.
- **`django` is a declared dependency** in `pyproject.toml` + `requirements.txt` but **never imported** in `src/main.py`. It is unused — treat it as cruft unless a purpose is confirmed.
- **No commands beyond `python src/main.py`**. The script is fully interactive (stdin prompts, 3 numbered modes). No CLI args.
- **`os.chdir` pattern**: The script `os.chdir()`s into the target download directory inside each mode, with `try/finally` to restore `os.getcwd()`. This means working directory changes during execution.
- **URL patterns**: Stickers use numeric IDs (`\d{6,9}`) under `/stickershop/product/`, emoji use alphanumeric IDs (`[a-zA-Z0-9]{23,25}`) under `/emojishop/product/`.
- **Download CDN**: Emoji from `stickershop.line-scdn.net`, stickers from `dl.stickershop.line.naver.jp`.
- **Batch mode** reads URLs from a `bdp.txt` file (default path). Each line can be a product URL or an author URL.

## Outdated documentation

- **README.md** and `docs/` reference standalone scripts (`dl.py`, `bd.py`, `bdp.py`) that **no longer exist**. All functionality is consolidated in `src/main.py`. The README docs are stale for the current codebase.

## What to NOT do

- Do not add tests, CI, linting, or type annotations — none exist and there are no conventions for them.
- Do not refactor `main.py` into a package layout unless explicitly asked — the project is intentionally a single file.
- Do not commit lockfile changes without a corresponding `uv add` or `uv lock` operation.
