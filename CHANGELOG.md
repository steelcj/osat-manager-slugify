# CHANGELOG

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- Fix: backtick and special character handling in bash wrapper
- Feat: Markdown title extraction (`slug file.md`)
- Feat: Sidecar metadata filename generation (`--sidecar`)
- Feat: Multilingual stopword presets

---

## [1.1.0] - 2026-09-25

### Changed
- Install layout follows OSAT Fluent: versioned app and venv under `~/.local/share/slug-tool/<version>/`, wrapper at `~/.local/bin/slug`, config at `~/.config/slug-tool/config.yml` (Windows: `%LOCALAPPDATA%` and `%APPDATA%`)
- `slugify_cli.py` reads the per-user config, falling back to `config.yml` beside the script

### Added
- `install-slug.py` manager with `--install`, `--switch`, `--status`, `--remove` and `--version`
- Windows wrapper template (`scripts/windows/slug-wrapper.cmd`), untested on real hardware
- `VERSION` file

### Removed
- Hard-coded `~/bin` wrapper (`scripts/nix/slug`), replaced by the rendered `scripts/nix/slug-wrapper`

## [1.0.0] — 2026-03-16

### Added
- CLI tool `slug` with Unix-style argument and stdin support
- Multilingual text handling via `python-slugify`
- YAML configuration file (`config.yml`)
- Python virtual environment isolation
- Bash wrapper (`scripts/nix/slug`)
- README and ROADMAP
