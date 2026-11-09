# 🚀 TCPING — TCP Ping Tool (Python + UV)

🇺🇸 **English** | 🇧🇷 [Português](README.pt-BR.md)

A robust command-line tool (CLI) to test **TCP** port connectivity. Unlike the traditional ping (ICMP), it checks whether specific services (web, SSH, databases, etc.) are accepting connections, reporting latency and stability metrics.

![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)
![UV](https://img.shields.io/badge/Managed%20by-UV-purple?logo=python)
![OS](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

<img width="773" height="400" alt="print-windows" src="https://github.com/user-attachments/assets/50027b2e-4dd6-47ed-a76a-b7cf68fd7efd" />

## ✨ Features

* **TCP handshake:** Measures the real response time of the service (SYN/SYN-ACK).
* **Advanced statistics:** Average, minimum, maximum and **jitter** (latency variation).
* **Count mode (`-c`):** Set a number of attempts or run forever.
* **Multiple targets:** Several hosts and ports at once, tested in parallel.
* **Scripting friendly:** Exit codes like `ping` and JSON output.
* **Installable as a command:** Via `uv tool`, available in any terminal as `tcping`.
* **Rich interface:** Uses the `Rich` library for tables and colors in the terminal.

---

## 🛠️ Prerequisites

* **`uv`** (ultra-fast Python package manager): required.
* **Git**: needed to install straight from GitHub (`git+https://...`) or from a clone. Without it, see [installing without Git](#installing-without-git).

### uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or, on any system, via `pip`:

```bash
pip install uv
```

### Git

Check whether it is installed with `git --version`. If it is not:

| System | Command |
|---|---|
| **Debian / Ubuntu / Linux Mint** | `sudo apt install git` |
| **Fedora** | `sudo dnf install git` |
| **macOS** | `xcode-select --install` |
| **Windows** | `winget install --id Git.Git -e` |

## 📦 Installation

Straight from GitHub, no clone needed:

```bash
uv tool install git+https://github.com/enricopablo/TCPing
```

Or from a local clone:

```bash
git clone https://github.com/enricopablo/TCPing.git
cd TCPing/
uv tool install --force .
```

### Installing without Git

If Git is not installed (error `Git executable not found`), install from the GitHub `.zip`:

```bash
uv tool install "tcping @ https://github.com/enricopablo/TCPing/archive/refs/heads/main.zip"
```

Done! The `tcping` command is available in any terminal (macOS, Linux and Windows).

> If the terminal cannot find the command, run `uv tool update-shell` and open a new terminal.

### 📍 Where `tcping` is installed

`uv tool` installs the executable (which must be on your `PATH`) and an isolated environment with the code and its dependencies:

| System | Executable | Isolated environment |
|---|---|---|
| **Windows** | `%USERPROFILE%\.local\bin\tcping.exe` | `%APPDATA%\uv\data\tools\tcping\` |
| **macOS** | `~/.local/bin/tcping` | `~/.local/share/uv/tools/tcping/` |
| **Linux** | `~/.local/bin/tcping` | `~/.local/share/uv/tools/tcping/` |

These paths may change according to environment variables (`UV_TOOL_BIN_DIR`, `UV_TOOL_DIR`, `XDG_BIN_HOME`, `XDG_DATA_HOME`). To check on your machine:

```bash
uv tool dir --bin   # executable folder
uv tool dir         # isolated environments folder
```

To try it without installing anything (requires Git):

```bash
uvx --from git+https://github.com/enricopablo/TCPing tcping google.com 443
```

### Upgrade / Uninstall

```bash
uv tool upgrade tcping      # installed from GitHub (git+https)
uv tool install --force .   # installed from a clone (after git pull)
uv tool uninstall tcping
```

Installed without Git (`.zip`)? To upgrade, repeat the install command with `--force --reinstall`:

```bash
uv tool install --force --reinstall "tcping @ https://github.com/enricopablo/TCPing/archive/refs/heads/main.zip"
```

## 🚀 Usage

```bash
tcping <host...> <port...> [options]
```

Examples:

```bash
# Basic test (runs until you press Ctrl+C)
tcping google.com 443

# 10 attempts with a 0.5s interval
tcping 1.1.1.1 80 -c 10 -i 0.5

# Final report only, without each attempt
tcping google.com 443 -c 5 -r
```

### 🎯 Multiple Targets

Pass as many hosts and ports as you like: **numbers are ports, everything else is a host**. `tcping` tests every combination, **in parallel**:

```bash
tcping web1 web2 443          # 2 targets: web1:443, web2:443
tcping google.com 80 443      # 2 targets: google.com:80, google.com:443
tcping web1 web2 80 443       # 4 targets: every combination
```

With more than one target, the output becomes a live-updating table with the last latency, statistics and the history of the last 10 attempts of each target. A side-by-side summary is shown at the end.

- `-c` sets how many attempts **each target** gets; `-i` is the interval from the start of one round to the start of the next (like `ping`). If a round takes longer than `-i`, the next one starts right away.
- A host that is not found is reported and the others keep being tested.

## 🤖 Scripting and Automation

### Exit codes

Like `ping`, `tcping` reports the result through its exit code:

| Code | Meaning |
|---|---|
| `0` | Every target had at least one successful connection |
| `1` | Some target had no successful connection |
| `2` | Usage error (including invalid `-c`, `-i` and `-t` values) or host not found |

With a single target, this means: `0` if it replied at least once, `1` if it never replied.

```bash
tcping db.local 5432 -c 3 -r && ./deploy.sh              # deploy only if the database replies
tcping db.local 5432 -c 3 -r || echo "Database down!"    # alert if it does not reply
tcping web1 web2 db 443 5432 -c 3 -r && ./deploy.sh      # only if ALL targets reply
```

### JSON output (`--json`)

Each event becomes one JSON line ([NDJSON](https://github.com/ndjson/ndjson-spec)), identified by the `type` field:

```bash
tcping google.com 443 -c 2 --json
```

```json
{"type": "attempt", "host": "google.com", "ip": "142.250.219.206", "port": 443, "seq": 1, "timestamp": "2026-11-08T21:32:39", "status": "open", "latency_ms": 17.52, "error": null}
{"type": "attempt", "host": "google.com", "ip": "142.250.219.206", "port": 443, "seq": 2, "timestamp": "2026-11-08T21:32:40", "status": "closed", "latency_ms": null, "error": "Timeout"}
{"type": "summary", "host": "google.com", "ip": "142.250.219.206", "port": 443, "family": "ipv4", "attempts": 2, "success": 1, "failed": 1, "success_rate": 50.0, "latency_ms": {"min": 17.52, "avg": 17.52, "max": 17.52, "jitter": 0.0}, "duration_s": 2.24}
```

- With multiple targets, there is one `summary` line **per target**, at the end; `seq` is the round number.
- With `-r`, only the `summary` lines are emitted.
- A host that is not found produces `{"type": "error", ..., "error": "Host not found"}` and exit code `2`; the other targets continue.
- Missing values (latency of a failed attempt, latency without any success) are `null`.

```bash
tcping google.com 443 -c 5 --json -r | jq .latency_ms.avg   # average latency
tcping google.com 443 --json >> history.jsonl               # continuous monitoring
```

## 📊 CLI Options

```text
Option      Short   Description                                 Default
--count     -c      Attempts per target (0 = infinite)          0
--interval  -i      Interval between rounds (seconds, >= 0)     1.0
--timeout   -t      Timeout per attempt (seconds, > 0)          2.0
            -4      Force IPv4                                  -
            -6      Force IPv6                                  -
--report    -r      Show only the final report                  -
--json              JSON output (one line per event)            -
--version   -V      Show the installed version                  -
--help      -h      Show the help                               -
```

### 🔍 Understanding the Output

`tcping` performs the **TCP three-way handshake**. The latency shown is the time between sending the `SYN` and receiving the `SYN-ACK`.

The host name is resolved (DNS) **only once**, before the first test, so DNS time is not included in the latency. The resolved IP is shown in the header, e.g. `google.com (142.250.79.46):443`. IPv4 and IPv6 are supported; use `-4` or `-6` to force one of them.

- 🟢 `OPEN`: the service replied and the connection was accepted.

- 🔴 `CLOSED`: the connection failed. The reason is shown in parentheses:
  - `Refused`: the host replied, but no service is listening on that port.
  - `Timeout`: no reply within the timeout (usually a firewall dropping packets).
  - `Network unreachable` / `Host unreachable`: there is no route to the destination.

- `Host not found`: the name could not be resolved (DNS).

- `Jitter`: latency variation. High values indicate an unstable route or an overloaded host.

## 📂 Project Structure

```text
.
├── src/tcping/
│   ├── __init__.py   # Package version
│   ├── __main__.py   # Enables `python -m tcping`
│   ├── cli.py        # Command-line interface (click) and attempt loop
│   ├── output.py     # Display: terminal (rich) or JSON
│   ├── probe.py      # DNS resolution and TCP connection test
│   ├── stats.py      # Statistics and run summary
│   └── target.py     # Targets: argument parsing and per-target statistics
├── tests/            # Automated tests (pytest)
├── main.py           # Shortcut: `uv run main.py <host> <port>`
├── CHANGELOG.md      # Version history
├── pyproject.toml    # Project settings and the `tcping` command
├── uv.lock           # Locked dependency versions
├── README.md         # Documentation (English)
└── README.pt-BR.md   # Documentation (Portuguese)
```

## 🧑‍💻 Development

```bash
uv sync                               # create the environment with the dependencies
uv run tcping google.com 443          # run the local code
uv run pytest                         # run the tests (no internet required)
uv tool install --editable --force .  # (optional) global `tcping` reflecting the local code
```

---
<p align="center">Obviously made with 🤖, human ingenuity 🤷🏻‍♂️, and a suspicious amount of tokens 🔥.</p>
