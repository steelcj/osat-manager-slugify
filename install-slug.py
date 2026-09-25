#!/usr/bin/env python3
"""install-slug.py -- manage the `slug` tool in user-space, OSAT Fluent style.

Installs the version in this checkout (see VERSION) into a versioned
directory with its own virtual environment, and renders a wrapper so `slug`
runs from anywhere. Follows the same layout as osat-fluent-python-tool.

Layout (Linux, macOS):
  app      ~/.local/share/slug-tool/<version>/slugify_cli.py
  venv     ~/.local/share/slug-tool/<version>/.venv/
  wrapper  ~/.local/bin/slug
  config   ~/.config/slug-tool/config.yml   (seeded once, never overwritten)

Layout (Windows):
  app      %LOCALAPPDATA%\\slug-tool\\<version>\\slugify_cli.py
  venv     %LOCALAPPDATA%\\slug-tool\\<version>\\.venv\\
  wrapper  %LOCALAPPDATA%\\Programs\\slug.cmd
  config   %APPDATA%\\slug-tool\\config.yml

XDG_DATA_HOME, XDG_BIN_HOME and XDG_CONFIG_HOME are honoured when set.

The venv is built with the interpreter running this script, so run it with
the Python you want the tool to use, for example a python-tool install:
  python3.12 install-slug.py --install

Usage:
  install-slug.py --install          Install this checkout's version and point the wrapper at it
  install-slug.py --switch VERSION   Point the wrapper at another installed version
  install-slug.py --status           Show installed and active versions
  install-slug.py --remove VERSION   Remove an installed version (not the active one)
  install-slug.py --version          Show this manager's version

Requires Python 3.8+ (standard library only) to run the manager itself.
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
TOOL_NAME = "slug-tool"
COMMAND = "slug"
APP_FILES = ("slugify_cli.py", "requirements.txt", "VERSION")
SEED_CONFIG = "config.yml"
MIN_PYTHON = (3, 8)


class InstallError(RuntimeError):
    """Raised for any condition that should stop the manager with a clear message."""


def log(message: str) -> None:
    print(f"[{TOOL_NAME}] {message}")


def fail(message: str) -> None:
    raise InstallError(message)


def manager_version() -> str:
    try:
        return (REPO_DIR / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        fail(f"VERSION file missing at {REPO_DIR / 'VERSION'} (repo checkout is incomplete)")


def refuse_root() -> None:
    if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() == 0:
        fail(f"refusing to run as root. {TOOL_NAME} installs entirely in user-space under $HOME.")
    if os.name == "nt":
        try:
            import ctypes

            if ctypes.windll.shell32.IsUserAnAdmin():
                fail(f"refusing to run as Administrator. {TOOL_NAME} installs entirely in user-space under %LOCALAPPDATA%.")
        except InstallError:
            raise
        except Exception:
            pass


class Paths:
    def __init__(self) -> None:
        self.is_windows = os.name == "nt"
        home = Path.home()
        if self.is_windows:
            local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
            roaming = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
            self.bin_dir = local / "Programs"
            self.tool_root = local / TOOL_NAME
            self.config_dir = roaming / TOOL_NAME
        else:
            self.bin_dir = Path(os.environ.get("XDG_BIN_HOME", home / ".local" / "bin"))
            self.tool_root = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")) / TOOL_NAME
            self.config_dir = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / TOOL_NAME

    @property
    def wrapper(self) -> Path:
        return self.bin_dir / (f"{COMMAND}.cmd" if self.is_windows else COMMAND)

    @property
    def config_file(self) -> Path:
        return self.config_dir / "config.yml"

    def version_dir(self, version: str) -> Path:
        return self.tool_root / version

    def venv_python(self, version: str) -> Path:
        venv = self.version_dir(version) / ".venv"
        return venv / "Scripts" / "python.exe" if self.is_windows else venv / "bin" / "python"

    def cli(self, version: str) -> Path:
        return self.version_dir(version) / "slugify_cli.py"

    def installed_versions(self) -> list:
        if not self.tool_root.is_dir():
            return []
        return sorted(p.name for p in self.tool_root.iterdir() if p.is_dir())

    def active_version(self):
        """Version the wrapper currently points at, or None."""
        try:
            content = self.wrapper.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        for version in self.installed_versions():
            if str(self.cli(version)) in content:
                return version
        return None


def make_owner_only(root: Path) -> None:
    if os.name == "nt":
        return
    for path in [root, *root.rglob("*")]:
        if path.is_symlink():
            continue
        try:
            if path.is_dir():
                path.chmod(stat.S_IRWXU)
            else:
                mode = stat.S_IRUSR | stat.S_IWUSR
                if os.access(path, os.X_OK):
                    mode |= stat.S_IXUSR
                path.chmod(mode)
        except OSError:
            continue


def run(cmd: list) -> None:
    result = subprocess.run([str(c) for c in cmd])
    if result.returncode != 0:
        fail(f"command failed ({result.returncode}): {' '.join(str(c) for c in cmd)}")


def render_wrapper(paths: Paths, version: str) -> Path:
    template_path = REPO_DIR / "scripts" / ("windows/slug-wrapper.cmd" if paths.is_windows else "nix/slug-wrapper")
    if not template_path.exists():
        fail(f"wrapper template missing: {template_path} (repo checkout is incomplete)")
    paths.bin_dir.mkdir(parents=True, exist_ok=True)
    template = template_path.read_text(encoding="utf-8")
    content = template.format(python=paths.venv_python(version), cli=paths.cli(version))
    newline = "\r\n" if paths.is_windows else "\n"
    with open(paths.wrapper, "w", encoding="utf-8", newline=newline) as handle:
        handle.write(content)
    if not paths.is_windows:
        paths.wrapper.chmod(stat.S_IRWXU)
    return paths.wrapper


def seed_config(paths: Paths) -> None:
    if paths.config_file.exists():
        log(f"keeping existing config: {paths.config_file}")
        return
    source = REPO_DIR / SEED_CONFIG
    if not source.exists():
        return
    paths.config_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, paths.config_file)
    log(f"seeded config: {paths.config_file}")


def warn_environment(paths: Paths) -> None:
    separator = ";" if paths.is_windows else ":"
    on_path = [Path(p) for p in os.environ.get("PATH", "").split(separator) if p]
    if paths.bin_dir not in on_path:
        log(f"warning: {paths.bin_dir} is not on PATH. Add it to run '{COMMAND}' from anywhere.")
        return
    found = shutil.which(COMMAND)
    if found and Path(found).resolve() != paths.wrapper.resolve():
        log(f"warning: '{COMMAND}' resolves to {found}, which shadows {paths.wrapper}.")
    legacy_wrapper = Path.home() / "bin" / "slug"
    legacy_dir = Path.home() / "bin" / "slugify-tool"
    if not paths.is_windows and (legacy_wrapper.exists() or legacy_dir.exists()):
        log("note: a pre-1.1.0 install is still present. Once the new one works, remove it with:")
        log(f"  rm -f {legacy_wrapper} && rm -rf {legacy_dir}")


def do_install(paths: Paths, force: bool) -> int:
    if sys.version_info < MIN_PYTHON:
        fail(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required to build the venv; running {sys.version.split()[0]}")
    version = manager_version()
    version_dir = paths.version_dir(version)

    if version_dir.exists() and not force:
        if paths.active_version() == version and paths.venv_python(version).exists():
            log(f"{version} is already installed and active. Pass --force to reinstall.")
            return 0
    if version_dir.exists():
        log(f"removing existing install at {version_dir}...")
        shutil.rmtree(version_dir)

    version_dir.mkdir(parents=True)
    for name in APP_FILES:
        source = REPO_DIR / name
        if not source.exists():
            fail(f"{source} missing (repo checkout is incomplete)")
        shutil.copy2(source, version_dir / name)

    log(f"creating venv with {sys.executable} (Python {sys.version.split()[0]})...")
    run([sys.executable, "-m", "venv", "--prompt", f"{TOOL_NAME}-{version}", version_dir / ".venv"])
    python = paths.venv_python(version)
    log("installing pinned requirements...")
    run([python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", version_dir / "requirements.txt"])

    make_owner_only(version_dir)
    seed_config(paths)
    wrapper = render_wrapper(paths, version)
    log(f"wrapper installed: {wrapper} -> {version}")
    warn_environment(paths)
    log(f"done. Try: {COMMAND} 'Référence API'")
    return 0


def do_switch(paths: Paths, version: str) -> int:
    if not paths.venv_python(version).exists():
        fail(f"{version} is not installed. Installed: {', '.join(paths.installed_versions()) or '(none)'}")
    render_wrapper(paths, version)
    log(f"active version is now {version}")
    return 0


def do_status(paths: Paths) -> int:
    active = paths.active_version()
    installed = paths.installed_versions()
    log(f"manager version: {manager_version()}")
    log(f"install root:    {paths.tool_root}")
    log(f"wrapper:         {paths.wrapper}{'' if paths.wrapper.exists() else ' (missing)'}")
    log(f"config:          {paths.config_file}{'' if paths.config_file.exists() else ' (missing)'}")
    if not installed:
        log("installed:       (none)")
    for version in installed:
        log(f"installed:       {version}{'  (active)' if version == active else ''}")
    return 0


def do_remove(paths: Paths, version: str) -> int:
    if version not in paths.installed_versions():
        fail(f"{version} is not installed.")
    if version == paths.active_version():
        fail(f"{version} is active. Switch to another version first, or remove the wrapper {paths.wrapper} by hand.")
    shutil.rmtree(paths.version_dir(version))
    log(f"removed {version}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Manage the '{COMMAND}' tool in user-space.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="install this checkout's version and activate it")
    group.add_argument("--switch", metavar="VERSION", help="point the wrapper at an installed version")
    group.add_argument("--status", action="store_true", help="show installed and active versions")
    group.add_argument("--remove", metavar="VERSION", help="remove an installed, inactive version")
    group.add_argument("--version", action="store_true", help="show this manager's version")
    parser.add_argument("--force", action="store_true", help="with --install, reinstall even if already current")
    args = parser.parse_args()

    try:
        if args.version:
            print(manager_version())
            return 0
        refuse_root()
        paths = Paths()
        if args.install:
            return do_install(paths, args.force)
        if args.switch:
            return do_switch(paths, args.switch)
        if args.status:
            return do_status(paths)
        return do_remove(paths, args.remove)
    except InstallError as exc:
        print(f"[{TOOL_NAME}] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
