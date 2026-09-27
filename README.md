<div align="center">

# muse-cli

Talk to your personal muse.ai AI agent from the terminal.

[![PyPI](https://img.shields.io/pypi/v/muse-cli?style=for-the-badge)](https://pypi.org/project/muse-cli/)
[![Python](https://img.shields.io/pypi/pyversions/muse-cli?style=for-the-badge)](https://pypi.org/project/muse-cli/)
[![Downloads](https://img.shields.io/pepy/dt/muse-cli?style=for-the-badge)](https://pepy.tech/project/muse-cli)
[![License: MIT](https://img.shields.io/github/license/nikships/muse-cli?style=for-the-badge)](https://github.com/nikships/muse-cli/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/nikships/muse-cli?style=for-the-badge)](https://github.com/nikships/muse-cli/stargazers)
[![Website](https://img.shields.io/badge/website-live-3fb950?style=for-the-badge)](https://muse-cli-site.web.app)

![muse-cli hero](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/hero.webp)

</div>

## What is this?

A command-line client for your personal muse.ai AI agent: chat from the terminal, automate it with scripts, and manage side chats, feed, goals, ideas, and sessions without opening a browser. It speaks the app's own gateway protocol directly: HTTPS auth, then an encrypted Noise-XX WebSocket to your personal VM.

- **Chat from the shell:** send a message and get the agent's reply back as JSON.
- **Script it:** every command prints JSON, so it pipes into `jq`, cron jobs, and other AI agents.
- **Full coverage:** named commands for the common tasks, plus a `raw` escape hatch for all 258 gateway methods.
- **Agent-ready:** ships an agent skill so coding agents can drive your muse.ai agent for you.

## Agents driving agents

Prompt a coding agent, it activates the muse-cli skill and runs read-only
commands for you. Live session below: a Droid worker runs `muse-cli status`
and `muse-cli goals`, then reports back.

![Droid agent using muse-cli to check status and goals](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/demo-agent.png)

## Agent Side-Chat Workflow

Give any terminal-based coding agent its own persistent Muse side chat for web research, browsing, and delegated tasks.

The `agent` command group wraps the existing `session-start`, `send --thread`, and `history --thread` commands with a local name-to-thread registry. Each agent name maps to one persistent side-chat thread, stored in `~/.config/muse-cli/agents.json` (mode 644, non-sensitive metadata only — no cookies, tokens, or message content).

```bash
muse-cli agent init opencode          # create or reuse a side chat
muse-cli agent list                   # show all agents + thread status
muse-cli agent send opencode "research X" --wait 120
muse-cli agent history opencode --limit 10
```

### Why dedicated side chats

- **Isolation:** each agent's context stays separate — no cross-contamination between OpenCode, Codex, and Claude Code conversations.
- **Persistence:** threads survive agent restarts; re-running `agent init` reuses the same thread.
- **Auditability:** `agent list` shows which threads are stale (deleted server-side) so you can rebind with `agent init`.
- **Simplicity:** no need to track thread IDs manually — the registry resolves names to threads automatically.

## Quick Start

```bash
uv tool install muse-cli      # or: pipx install muse-cli   /   pip install muse-cli
```

The command is `muse-cli`. The name `muse` belongs to Muse Code on many machines.

Want the agent skill too? The installer sets up the CLI and copies the skill
to `~/.agents/skills/muse-cli`:

```bash
curl -fsSL https://raw.githubusercontent.com/nikships/muse-cli/main/install.sh | bash
```

Upgrade with `muse-cli update`. In a terminal it also checks PyPI once a day and, when a newer release exists, prints that command on stderr. It does not upgrade itself. Set `MUSE_NO_UPDATE_CHECK=1` to silence the notice. The check stays quiet when output is piped or `CI` is set. Remove with `uv tool uninstall muse-cli`.

Logging in is a separate one-time step. Chrome shares its cookies after you
turn on remote debugging. Follow [Log in once](#log-in-once) before running
any other command.

## Log in once

muse-cli borrows the login you already have in Chrome, saves those cookies
to `~/.config/muse-cli/cookies.txt` (mode `600`, only your user can read it),
and after that talks to muse.ai directly. Access tokens are fetched fresh
on every command. When a command later says the cookies expired, repeat this
section.

Do the steps in order. Each one checks itself before you continue.

### 1. Install the cookie reader

`auth export` uses [agent-browser](https://github.com/vercel-labs/agent-browser)
to read Chrome's cookies. That package comes from npm, so you need Node.js first.

```bash
node --version    # if this fails, install Node.js LTS from https://nodejs.org
                  # and open a new terminal
npm i -g agent-browser
agent-browser --version
```

`npm i -g` needs permission to write to npm's global bin directory. If it
errors with `EACCES`, pick one and use it from then on: configure an
[npm prefix you own](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally),
or run the install with the same rights you use for other global npm tools.
Then check `command -v agent-browser` prints a path.

### 2. Let Chrome share cookies

Open **Google Chrome**, the same profile you use for muse.ai. Paste this in
the address bar:

```
chrome://inspect/#remote-debugging
```

Turn on remote debugging. The checkbox reads **Allow remote debugging for
this browser instance**. Leave Chrome open.

Turn this on while Chrome is already open and muse.ai is loaded. The export
can see that window only after the switch is on. The page is in Chrome 144
and newer.

Stay in this window. Starting a second Chrome with
`--remote-debugging-port` opens a different profile, and that profile does
not have your muse.ai login.

### 3. Be logged in, on a muse.ai tab

In that same Chrome window, open https://muse.ai/ and log in. Leave the tab
open. The exporter reads whichever tab is active, so the muse.ai tab has to
be the one in front when you run the next command.

### 4. Save the login

```bash
muse-cli auth export
```

Chrome may ask to allow the debugging connection. Click **Allow**. If the
command already failed, run it again after you click Allow.

Success looks like this (the count varies):

```
saved 12 muse.ai cookies to /home/you/.config/muse-cli/cookies.txt
```

The command prints the fix on the failure itself. These are the ones it
recognizes:

| What it says | What to do |
| --- | --- |
| No running Chrome / remote debugging | The switch in step 2 is off. Turn it on in the Chrome you already have open, then run the command again. |
| No muse.ai tab | Step 3. Open https://muse.ai/ in that same window and leave the tab open. |
| No `hatch_sess` | The tab is open and you are logged out. Log in, then export again. The cookies file already on disk is left as it was. |
| `agent-browser` is not installed | Step 1. `node --version`, then `npm i -g agent-browser`, then a new terminal. |
| Daemon already running | A previous attempt is stuck. `agent-browser close`, then `muse-cli auth export`. |

### 5. Check the connection

```bash
muse-cli status
```

You get JSON with your VM id, how many chats you have, the unread count, and
your identity. That means install and login both worked.

### Copy cookies by hand

Use this when you don't have Node, or you don't want remote debugging on.

1. In Chrome, open https://muse.ai/ and log in.
2. Open DevTools (F12, or Ctrl+Shift+I) → **Application** → **Cookies** → `https://muse.ai`.
3. Copy the cookies onto one line. `hatch_sess` has to be there. Separate cookies with `; ` (semicolon, space). A Netscape cookie jar (what curl writes) and a JSON object such as `{"hatch_sess": "..."}` also work.

```bash
mkdir -p ~/.config/muse-cli
printf '%s\n' 'hatch_sess=the-value-from-devtools; other_cookie=other_value' > ~/.config/muse-cli/cookies.txt
chmod 600 ~/.config/muse-cli/cookies.txt
muse-cli status
```

## Usage

```bash
muse-cli threads                                  # main chat + side chats
muse-cli history --limit 5                        # recent messages
muse-cli history --thread <session-id> --limit 5  # one side chat
muse-cli send "summarize my unread" --wait 120    # send + wait for the reply
muse-cli watch --timeout 60                       # tail live agent events

muse-cli feed --limit 5
muse-cli feed-react <unit-id> love
muse-cli goals
muse-cli ideas
muse-cli idea-exec <idea-id>                      # agent acts on the idea

muse-cli session-start --title "trip planning"    # new side chat
muse-cli session-rename <id> "new title"
muse-cli session-archive <id>                     # also: pin, unpin, unarchive, delete
muse-cli seen <thread-id>
muse-cli wake
muse-cli raw <method> --body '{}'                 # escape hatch: any of 258 gateway methods
```

Every command prints JSON. Your VM is auto-discovered from your session, and a
random device id is generated on first run.

Pipe it into other tools:

```bash
muse-cli send "what's on my calendar today?" | jq -r .reply.text
```

## Agent commands

The `agent` command group manages named side-chat threads. It wraps the existing `session-start`, `send --thread`, and `history --thread` commands — those remain unchanged and fully functional on their own.

```bash
muse-cli agent init <name> [--title "optional title"]
muse-cli agent list
muse-cli agent send <name> <text> [--wait N]
muse-cli agent history <name> [--limit N] [--raw]
```

- `init` is idempotent: if the name already exists and its thread is still alive, it reuses it; otherwise it creates a fresh side chat.
- `send` and `history` resolve the name to a thread ID automatically. Unknown names exit with code 2; stale threads (deleted server-side) exit with code 3.
- The registry lives at `~/.config/muse-cli/agents.json` (mode 644). It stores only names, thread IDs, titles, and timestamps — never cookies, tokens, or message content.
- Works on Windows, macOS, and Linux. Set `MUSE_CLI_CONFIG_DIR` to override the config directory.

### OpenCode example

```bash
# In an OpenCode session, give the agent its own persistent side chat:
muse-cli agent init opencode --title "OpenCode research"

# Send a research task and wait for the reply:
muse-cli agent send opencode "Find the latest stable release of curl_cffi and summarize breaking changes" --wait 120

# Check the conversation history:
muse-cli agent history opencode --limit 5
```

### Codex CLI example

```bash
# From a Codex CLI session:
muse-cli agent init codex --title "Codex delegated tasks"

# Delegate a browsing task:
muse-cli agent send codex "Browse https://example.com and extract the pricing table" --wait 90

# Review what the agent found:
muse-cli agent history codex --limit 3
```

### Claude Code example

```bash
# From a Claude Code session:
muse-cli agent init claude --title "Claude web research"

# Delegate a long-running research task:
muse-cli agent send claude "Research the top 3 vector databases for Python and compare their licenses" --wait 180

# Check results:
muse-cli agent history claude --limit 5
```

### Gemini CLI example

The pattern is the same for any terminal-based agent that can run shell commands:

```bash
muse-cli agent init gemini --title "Gemini research"
muse-cli agent send gemini "Search for recent changes to the Python GIL" --wait 120
muse-cli agent history gemini --limit 5
```

The thread ID is auto-resolved from the local registry — the agent never needs to know or track it. The underlying `send --thread`, `session-start`, and `history --thread` commands remain fully functional for direct use.

## How it works

![how muse-cli connects](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/how-it-works.webp)

![muse-cli connection flow](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/flow.webp)

See [docs/PROTOCOL.md](https://github.com/nikships/muse-cli/blob/main/docs/PROTOCOL.md)
for the full protocol notes, including the method table and the server quirks
found during reverse engineering.

## Documentation

| Resource | Description |
|----------|-------------|
| [skills/muse-cli/SKILL.md](https://github.com/nikships/muse-cli/blob/main/skills/muse-cli/SKILL.md) | Agent skill: install check, auth setup, command reference |
| [docs/PROTOCOL.md](https://github.com/nikships/muse-cli/blob/main/docs/PROTOCOL.md) | Gateway protocol reference: auth chain, Noise transport, framing, method quirks |
| [routes.json](https://github.com/nikships/muse-cli/blob/main/src/muse_cli/routes.json) | All 258 gateway methods with paths and services |
| `muse-cli raw --help` | Escape hatch for calling any gateway method directly |

## Development

```bash
git clone https://github.com/nikships/muse-cli.git
cd muse-cli
uv run muse-cli --help
```

```
muse-cli/
assets/              README artwork (generated with Muse Image)
docs/PROTOCOL.md     protocol reference for re-derivation
skills/muse-cli/     agent skill
src/muse_cli/
  cli.py             argument parsing and all commands
  gateway.py         gateway client (auth, Noise transport, subscriptions)
  routes.json        258 gateway methods extracted from the web client
  desc0.bin          protobuf descriptors for the wire framing
  desc1.bin
install.sh           CLI + skill installer
pyproject.toml
```

## Setup notes

- Login is the [Log in once](#log-in-once) section above. Cookies live at
  `~/.config/muse-cli/cookies.txt` (mode 600). Access and gateway tokens are
  fetched fresh on every run.
- `auth export` reads those cookies from Google Chrome through
  [agent-browser](https://github.com/vercel-labs/agent-browser). Chrome has
  to be open, with remote debugging on
  (`chrome://inspect/#remote-debugging`) and a logged-in muse.ai tab in front.
- Respect muse.ai's terms and rate limits. Internal APIs are unversioned and
  can change; if calls fail, re-derive from a fresh app bundle.

## Contributing

Issues and PRs welcome. If the protocol drifts, the most useful contribution
is a note of which method broke and the new server error text.

<a href="https://github.com/nikships/muse-cli/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nikships/muse-cli" />
</a>

## Referral code

An optional referral code exists: `W09QZF`. It is **not required** to use muse-cli or any of its features.

> **Disclaimer:** Verification of reward terms via direct Muse browsing was blocked by organization policy on 2026-09-27. Reward terms (quantity, eligibility, period) are unverified and not stated here. Check muse.ai directly for current terms.

## Credits

Based on / forked from [nikships/muse-cli](https://github.com/nikships/muse-cli) by [Nik](https://github.com/nikships). Original MIT License preserved.

The agent side-chat workflow wraps the existing `session-start`, `send --thread`, and `history --thread` commands — it does not reimplement or invent new gateway methods.

## License

MIT. See [LICENSE](https://github.com/nikships/muse-cli/blob/main/LICENSE).

---

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=nikships/muse-cli&type=Date)](https://star-history.com/#nikships/muse-cli&Date)

</div>
