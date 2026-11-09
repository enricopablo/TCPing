# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-11-08

### Changed
- **The whole program is now in English**: output, `--help`, error messages (including the `error` field in JSON), code comments and documentation. Scripts that compare message text must be updated (e.g. `OPEN`/`CLOSED`, `Refused`, `Host not found`). JSON keys, `status` values and exit codes are unchanged.
- `-i` is now counted from the **start** of one round to the start of the next (like `ping`). A round longer than the interval starts the next one right away. Before, the wait only began after the round ended (e.g. `-t 2 -i 1` with a timeout = 3s cycles).
- Ctrl+C exits immediately, without waiting for pending connections (up to `-t` seconds before).
- Ctrl+C in the middle of a round keeps the attempts that already finished in the summary.
- README in English; Portuguese version in `README.pt-BR.md`.
- README: repository renamed from `TCP-Ping` to `TCPing` in links and commands.
- README: Git listed as a prerequisite for installing from GitHub, plus installation and upgrade without Git (from the GitHub `.zip`).

### Fixed
- Invalid option values are now usage errors (exit code `2`) before any test: `-c` below 0 (ran nothing), `-i` below 0 (aborted after the first round) and `-t` 0 or below (every attempt failed with "Operation now in progress").

## [0.4.0] - 2026-11-08

### Added
- Multiple targets in one run: numbers are ports, everything else is a host, and every combination is tested (`tcping web1 web2 80 443` = 4 targets).
- Targets are tested in parallel in each round.
- With more than one target: live-updating table (last latency, min/avg/max, jitter and the last 10 attempts) and a side-by-side summary at the end.
- Port validation (1 to 65535) and usage errors for a missing host or port.
- New `target.py` module.

### Changed
- `-c` is now the number of attempts **per target**, and `-i` the interval between rounds.
- Exit code `0` requires **every** target to have replied at least once. With one target, nothing changes.
- A host not found in a list of targets no longer stops the others; the run ends with exit code `2`.
- JSON: `attempt` lines now include `host`, `ip` and `port`, and there is one `summary` per target.

### Fixed
- JSON: `jitter` was `0` (integer) with a single attempt; it is now `0.0`.

## [0.3.0] - 2026-11-08

### Added
- Exit codes like `ping`: `0` if at least one connection succeeded, `1` if none did, `2` for usage errors or host not found.
- `--report` / `-r`: shows only the header and the final report, without the attempts.
- `--json`: NDJSON output with `attempt`, `summary` and `error` events (with `-r`, only `summary`).
- Automated tests with `pytest` (`uv run pytest`), no internet required.
- `--help`: examples for `-r` and `--json`.
- `-h` shortcut for `--help`.
- README: "Scripting and Automation" section and a table with installation paths per operating system.

### Changed
- Display separated from measurement (new `output.py` module, with terminal and JSON output).
- An unexpected error during the run exits with code `2`, after showing the summary.

## [0.2.0] - 2026-11-08

### Added
- Installation as a global `tcping` command via `uv tool install` (straight from GitHub or from a local clone).
- `--version` / `-V`.
- Usage examples in `--help`.
- `-4` and `-6` to force IPv4 or IPv6.
- IPv6 support (addresses shown as `[::1]:443`).
- Resolved IP shown in the header, e.g. `google.com (142.250.79.46):443`.
- Run with `python -m tcping`.

### Changed
- Code reorganized into the `src/tcping/` package (`cli.py`, `probe.py`, `stats.py`). The root `main.py` is now just a shortcut for `uv run main.py`.
- Project renamed to `tcping`.
- DNS is resolved only once before testing: latency now measures only the TCP handshake.
- Failures show the real reason: refused, timeout, network unreachable, host unreachable.
- A nonexistent host is reported once ("host not found") and exits with code 2.
- The terminal screen is no longer cleared on start.
- README rewritten with the new installation, upgrade and removal methods.

### Fixed
- Latency shown for failed attempts (now shows `-`).
- Summary showed `0.00 ms` latency and jitter when no attempt succeeded (now shows `-`).
- Missing tool description in `--help`.
- Header showed "1 attempts" (now "1 attempt").
- README: Python version badge (3.13+), `uv` install commands with `\|` and typos.

### Removed
- Writing logs to files (`logs/` folder) and the `--output` / `-o` option.
- Alias instructions (`tping`) in the README, replaced by installation via `uv tool`.

## [0.1.0] - 2026-03-07

### Added
- First version: `main.py` script run with `uv run`.
- TCP connectivity test with latency, minimum, average, maximum and jitter.
- `--count`, `--interval`, `--timeout` and `--output` options.
- Logs in `logs/tcp_ping_HOST_PORTA.log`, in append mode.
- Screen cleared on start (Windows and Unix).
- `rich` interface and use through the `tping` alias.

[0.5.0]: https://github.com/enricopablo/TCPing/compare/ff132ee...HEAD
[0.4.0]: https://github.com/enricopablo/TCPing/compare/781c1da...ff132ee
[0.3.0]: https://github.com/enricopablo/TCPing/compare/781c1da...ff132ee
[0.2.0]: https://github.com/enricopablo/TCPing/compare/781c1da...ff132ee
[0.1.0]: https://github.com/enricopablo/TCPing/tree/781c1da
