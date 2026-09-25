---
dc:title: "Runbook: Cutting and Publishing Releases"
dcterms:version: "0.1.0"
dc:creator: "Christopher Steel"
dc:contributor: "Claude (Anthropic)"
dc:subject:
  - "devops"
  - "release"
  - "versioning"
  - "changelog"
  - "runbook"
dc:description: >
  How to set up release management in a fresh repository and then cut and
  publish every release: bootstrap VERSION, keep a CHANGELOG, cut with
  cut-release.py, push, and publish with publish-release.py.
dc:publisher: "UniversalCake"
dcterms:created: "2026-08-10"
dcterms:modified: "2026-08-10"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "runbook--cutting-and-publishing-releases"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel / UniversalCake.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: ""
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.1.0"
    date: "2026-08-10"
    author: "Christopher Steel"
    notes: >
      Initial version. Generalized the initial-release note into a reusable
      runbook covering first-time setup (bootstrap VERSION at 0.0.0 and cut the
      first release) and the recurring cut, push, and publish ceremony, with
      the real command output from the site-blankstudio.com v0.1.0 release as
      worked examples.
---

# Runbook: Cutting and Publishing Releases

Version: 0.1.0
Status: Draft
Style Guide: style-guide--plain-language-for-general-audiences

## Abstract

This runbook covers release management end to end: setting it up once in a fresh repository, then cutting and publishing every release afterward. It documents the three scripts synced from the `sat-doc-automa` canonical project — `bump-version.py`, `cut-release.py`, and `publish-release.py` — and the two files they operate on, `VERSION` and `CHANGELOG.md`. The worked examples are the real output from the `site-blankstudio.com` `v0.1.0` release.

## How the pieces fit

The repository version is a single semantic version in the root `VERSION` file, authoritative and independent of `package.json`. Changes are logged by hand under `## [Unreleased]` in `CHANGELOG.md` (Keep a Changelog format). Document versions under `docs/en/docs/` carry their own version lines and are not touched by any of this.

Three scripts, each doing one thing, live at the repository root:

- `bump-version.py` writes the next semantic version into `VERSION`, and nothing else.
- `cut-release.py` runs the release ceremony: bump (via `bump-version.py`), roll `## [Unreleased]` into a dated `## [X.Y.Z]` section, commit only `VERSION` and `CHANGELOG.md`, tag `vX.Y.Z`, and stop before push.
- `publish-release.py` builds a deterministic tarball for an already-pushed tag, writes `SHA256SUMS`, optionally GPG-signs it, and publishes through a backend (`gh` for GitHub, auto-detected; or `dir` for a plain directory).

Pushing sits deliberately between cutting and publishing, as a human act.

## Prerequisites

- The three scripts present at the repository root (synced from canonical).
- Python 3 with PyYAML available.
- For the GitHub backend: the `gh` CLI installed and authenticated once with `gh auth login`.
- Optional: a GPG secret key, if you want signed checksums. Without one, publishing proceeds unsigned rather than failing.

## First-time setup (once per repository)

A new repository has the scripts but not the two files they read. Bootstrap them, then cut the first release.

Create the `VERSION` file at `0.0.0`. It is intentionally one below the first release you intend to cut, because `cut-release.py` bumps before it tags — so the first cut moves `0.0.0` to your first real version.

```bash
echo "0.0.0" > VERSION
```

Ensure `CHANGELOG.md` exists with a `## [Unreleased]` section that already lists what the first release contains (the entries are always written by hand; the scripts never compose prose).

Commit the project so `VERSION` is clean — `cut-release.py` refuses to start on an uncommitted `VERSION`, treating it as a half-done release.

```bash
git add -A
git commit -m "Initial project state"
```

Cut the first release with an explicit version. From `0.0.0`, this sets `VERSION` to `0.1.0`, rolls `## [Unreleased]` into `## [0.1.0] - <today>`, commits those two files, and tags `v0.1.0`.

```bash
python3 cut-release.py 0.1.0
```

Push the commit and the tag, then publish. From here on it is identical to every later release, described next.

```bash
git push && git push origin v0.1.0
python3 publish-release.py
```

## Cutting a release (every time)

Write the changelog first. As work happens, add entries by hand under `## [Unreleased]` in `CHANGELOG.md`, grouped `Added` / `Changed` / `Fixed`. Commit your actual work as normal — `cut-release.py` only ever commits `VERSION` and `CHANGELOG.md`, never your other changes.

Then cut. Choose the bump by the nature of the changes:

```bash
python3 cut-release.py patch    # 0.1.0 -> 0.1.1
python3 cut-release.py minor    # 0.1.1 -> 0.2.0
python3 cut-release.py major    # 0.2.0 -> 1.0.0
python3 cut-release.py 0.3.2    # or set an explicit version
```

`cut-release.py` stops before pushing. Push the commit and its tag deliberately:

```bash
git push && git push origin vX.Y.Z
```

A successful first push of a new repository and tag looks like this:

```text
To github.com:steelcj/site-blankstudio.com.git
 * [new branch]      main -> main
To github.com:steelcj/site-blankstudio.com.git
 * [new tag]         v0.1.0 -> v0.1.0
```

## Publishing a release (every time)

With the tag on the remote, publish. On a GitHub remote the backend is auto-detected; `publish-release.py` builds the tarball twice and refuses to publish if the bytes differ (the determinism gate), writes `SHA256SUMS`, signs if a key is available, and creates the release.

```bash
python3 publish-release.py
```

Worked example from `v0.1.0`, publishing unsigned because no GPG key was present:

```text
[publish-release] backend: gh, tag v0.1.0 verified locally and on origin
[publish-release] built: site-blankstudio.com-0.1.0.tar.gz (1346 bytes, sha256 d6639d9b49e30426…, deterministic)
[publish-release] gpg or a secret key is unavailable; publishing unsigned (allowed, never blocking).

[publish-release] published v0.1.0 via gh:
  https://github.com/steelcj/site-blankstudio.com/releases/tag/v0.1.0
```

Useful variations:

```bash
python3 publish-release.py --dry-run                 # build and check, publish nothing
python3 publish-release.py --backend dir --target DIR # publish to a plain directory
python3 publish-release.py --no-sign                 # skip GPG even if a key exists
python3 publish-release.py --sign                    # require GPG; fail if no key
```

## When a script refuses

The scripts fail closed on purpose, so a refusal is information, not an obstacle.

`cut-release.py` refuses when `VERSION` has uncommitted changes (a half-done release is finished by hand, not stacked on), when `## [Unreleased]` is empty (nothing to release), or when the target tag already exists (tags are never reused — fix forward with the next number).

`publish-release.py` refuses when there is no tag for the current `VERSION` (cut first), when the tag's content disagrees with `VERSION`, when the tag is not on the remote (push first), when no backend matches the remote, when the release already exists, or when the archive bytes are not reproducible.

## License

This document, *Runbook: Cutting and Publishing Releases*, by **Christopher Steel**, with AI assistance from **Claude (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## Changelog

| Version | Status | Notes |
| --- | --- | --- |
| 0.1.0 | Draft | Initial version; generalized the initial-release note into a reusable setup-and-release runbook with worked examples from the v0.1.0 release |
