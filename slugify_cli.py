#!/usr/bin/env python3

import os
import sys
import argparse
import yaml
from pathlib import Path
from slugify import slugify


# ------------------------------------------------------------------------------
# Built-in defaults (fallback)
# ------------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "lowercase": True,
    "separator": "-",
    "ascii": True,
    "max_length": None,
    "stopwords": [],
}


# ------------------------------------------------------------------------------
# Locate the per-user config file
# ------------------------------------------------------------------------------

def user_config_path():
    """Per-user config written by install-slug.py.

    Linux/macOS: $XDG_CONFIG_HOME/slug-tool/config.yml (default ~/.config)
    Windows:     %APPDATA%\\slug-tool\\config.yml
    """

    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / "slug-tool" / "config.yml"


# ------------------------------------------------------------------------------
# Load default config: per-user file, else config.yml beside this script
# (the latter keeps running straight from a checkout working)
# ------------------------------------------------------------------------------

def load_script_config():

    candidates = [
        user_config_path(),
        Path(__file__).resolve().parent / "config.yml",
    ]

    for config_file in candidates:
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

    return {}


# ------------------------------------------------------------------------------
# Load user config
# ------------------------------------------------------------------------------

def load_user_config(path):

    if not path:
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


# ------------------------------------------------------------------------------
# Merge configs
# ------------------------------------------------------------------------------

def build_config(user_config):

    config = DEFAULT_CONFIG.copy()

    config.update(load_script_config())
    config.update(user_config)

    return config


# ------------------------------------------------------------------------------
# Input handling
# ------------------------------------------------------------------------------

def read_input(args):

    if args:
        return " ".join(args)

    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return data

    return None


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Convert text into a URL-safe slug.",
        epilog=(
            "Tip: use single quotes to safely pass strings containing\n"
            "backticks or other shell-special characters:\n\n"
            "  slug 'What belongs in `trust_boundary.yml`'\n\n"
            "Double quotes do NOT protect backticks from shell expansion."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "text",
        nargs="*",
        help="Text to slugify (use single quotes for special characters)"
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Optional user config YAML"
    )

    args = parser.parse_args()

    text = read_input(args.text)

    if not text:
        parser.print_help()
        sys.exit(0)

    user_config = load_user_config(args.config)
    config = build_config(user_config)

    result = slugify(
        text,
        lowercase=config["lowercase"],
        separator=config["separator"],
        max_length=config["max_length"],
        stopwords=config["stopwords"],
        allow_unicode=not config["ascii"],
    )

    print(result)


if __name__ == "__main__":
    main()
