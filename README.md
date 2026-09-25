# tool-python-slugify

## Description

A lightweight command-line tool for generating URL-safe slugs from text.

This tool is designed for multilingual documentation workflows and static site
generation systems where consistent slug creation is important for:

- filenames
- URLs
- metadata identifiers
- sidecar metadata files

The tool supports configuration via a YAML file and works naturally with
Unix-style pipelines.

---

## Features

- CLI tool with Unix-style behavior
- Supports both arguments and `stdin`
- Multilingual text support
- Configurable slug rules via YAML
- Uses the `python-slugify` library
- Runs inside an isolated Python virtual environment
- Suitable for static site generators and documentation systems

---

## Installation

The tool installs into user-space with `install-slug.py`, following the same layout as the OSAT Fluent python-tool. No root or Administrator privilege is needed, and the manager refuses to run with it.

Requirements: Python 3.8 or later to run the manager, with working `venv` and `pip`. The venv is built from whichever interpreter runs the manager, so to use a python-tool install, run it with that interpreter (for example `python3.12`).

### Requirements

```bash
apt install python3.12-venv
```

### Linux and macOS

```bash
git clone https://github.com/steelcj/tool-python-slugify.git
cd tool-python-slugify
python3 install-slug.py --install
```

Make sure `~/.local/bin` is on your `PATH`. The manager warns if it is not, or if another `slug` earlier on `PATH` shadows the new one.

### Windows

```powershell
git clone https://github.com/steelcj/tool-python-slugify.git
cd tool-python-slugify
python install-slug.py --install
```

The wrapper lands in `%LOCALAPPDATA%\Programs`, which is not on `PATH` by default. Add it to your user `PATH`, then open a new terminal. Windows support is untested on real hardware so far.

### Managing versions

```
install-slug.py --install          Install this checkout's version and activate it
install-slug.py --switch VERSION   Point the wrapper at another installed version
install-slug.py --status           Show installed and active versions
install-slug.py --remove VERSION   Remove an installed, inactive version
install-slug.py --version          Show the manager's version
```

### Upgrading from 1.0.x

Earlier versions installed to `~/bin/slug` and `~/bin/slugify-tool`. After installing 1.1.0 and confirming `slug` works, remove the old install:

```bash
rm -f ~/bin/slug && rm -rf ~/bin/slugify-tool
```

If you customised `~/bin/slugify-tool/config.yml`, copy it to `~/.config/slug-tool/config.yml` first.

## Detailed Installation, Usage and Configuration

[How to Install and Use a Multilingual Slugify Tool with Python Virtual Environment](docs/how-to-install-and-use-the-multilingual-slugify-tool.md)

## Usage

### Slugify text

```
slug "Référence API"
```

Output:

```
reference-api
```

---

### Pipe input

```
echo "Accessibilité numérique" | slug
```

Output:

```
accessibilite-numerique
```

---

### File input

```
cat title.txt | slug
```

---

## Configuration

Default behavior is controlled by the per-user `config.yml` (see Installed Layout).

Example configuration:

```yaml
lowercase: true
separator: "-"
ascii: true
max_length: 80
stopwords:
  - de
  - la
  - les
```

### Configuration Options

| Option     | Description                         |
| ---------- | ----------------------------------- |
| lowercase  | Convert text to lowercase           |
| separator  | Character used between words        |
| ascii      | Remove accents and convert to ASCII |
| max_length | Optional maximum slug length        |
| stopwords  | Words to remove from slug           |

---

## Example

Input:

```
slug "Référence de la documentation API"
```

Output:

```
reference-documentation-api
```

---

## Installed Layout

Linux and macOS:

```
~/.local/share/slug-tool/<version>/slugify_cli.py
~/.local/share/slug-tool/<version>/.venv/
~/.local/bin/slug                              (wrapper)
~/.config/slug-tool/config.yml                 (seeded once, never overwritten)
```

Windows:

```
%LOCALAPPDATA%\slug-tool\<version>\slugify_cli.py
%LOCALAPPDATA%\slug-tool\<version>\.venv\
%LOCALAPPDATA%\Programs\slug.cmd                (wrapper)
%APPDATA%\slug-tool\config.yml
```

`XDG_DATA_HOME`, `XDG_BIN_HOME` and `XDG_CONFIG_HOME` are honoured when set. Config precedence is built-in defaults, then the per-user `config.yml`, then any file passed with `--config`.

## Future Improvements

Potential enhancements:

- automatic slug generation from Markdown titles
- multilingual stopword presets config example
- CI integration for documentation workflows (see SAT project)

---

## Dependencies

- Python 3.10+
- python-slugify
- PyYAML

---

## License

This project is released under the MIT License.
