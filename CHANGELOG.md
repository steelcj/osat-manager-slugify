# CHANGELOG

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Planned work lives in ROADMAP.md.

## [Unreleased]

## [1.1.0] - 2026-09-25

### Changed
- Repository renamed from `tool-python-slugify` to `osat-manager-slugify`
- Install layout follows OSAT Fluent: versioned app and venv under `~/.local/share/slug-tool/<version>/`, wrapper at `~/.local/bin/slug`, config at `~/.config/slug-tool/config.yml` (Windows: `%LOCALAPPDATA%` and `%APPDATA%`)
- `slugify_cli.py` reads the per-user config, falling back to `config.yml` beside the script

### Added
- `install-slug.py` manager with `--install`, `--switch`, `--status`, `--remove` and `--version`
- Windows wrapper template (`scripts/windows/slug-wrapper.cmd`)
- `VERSION` file, and release management through the shared sat-doc-automa ceremony

### Removed
- Hard-coded `~/bin` wrapper (`scripts/nix/slug`), replaced by the rendered `scripts/nix/slug-wrapper`

## [1.0.0] - 2026-03-16

### Added
- CLI tool `slug` with Unix-style argument and stdin support
- Multilingual text handling via `python-slugify`
- YAML configuration file (`config.yml`)
- Python virtual environment isolation
- Bash wrapper (`scripts/nix/slug`)
- README and ROADMAP
