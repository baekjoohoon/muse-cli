"""Agent side-chat workflow: thin wrapper over session features.

Manages a registry of named agents, each bound to a side-chat thread.
Config stored at <CONFIG_DIR>/agents.json.
"""
import json
import os
import re
import tempfile

AGENT_NAME_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')


def validate_agent_name(name):
    """Validate and normalize an agent name. Returns normalized name or raises ValueError."""
    key = name.strip().lower()
    if not AGENT_NAME_RE.match(key):
        raise ValueError(
            f"invalid agent name '{name}': must match ^[a-z0-9][a-z0-9_-]{{0,63}}$"
        )
    return key


def get_config_dir():
    """Return the config directory, honoring MUSE_CLI_CONFIG_DIR env override."""
    env = os.environ.get("MUSE_CLI_CONFIG_DIR")
    if env:
        return os.path.expanduser(env)
    return os.path.expanduser("~/.config/muse-cli")


def agents_file():
    """Return the path to the agents.json file."""
    return os.path.join(get_config_dir(), "agents.json")


def load_agents():
    """Load the agents registry. Returns {"version": 1, "agents": {...}}."""
    path = agents_file()
    if not os.path.exists(path):
        return {"version": 1, "agents": {}}
    try:
        with open(path) as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or not isinstance(data.get("agents"), dict):
            return {"version": 1, "agents": {}}
        return data
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "agents": {}}


def save_agents_atomic(data):
    """Save the agents registry atomically using mkstemp + os.replace."""
    path = agents_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".agents.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def resolve_thread(name, gw=None):
    """Resolve an agent name to its thread_id.

    Returns (thread_id, stale) where stale=True if the thread no longer exists.
    Raises KeyError if agent is unknown.
    """
    agents = load_agents()
    key = validate_agent_name(name)
    if key not in agents["agents"]:
        raise KeyError(key)
    entry = agents["agents"][key]
    thread_id = entry.get("thread_id")
    if not thread_id:
        raise KeyError(key)

    # Check if thread is still valid
    stale = False
    if gw is not None:
        try:
            sessions = gw.call_json("sessions.list")
            session_ids = {s.get("session_id") for s in sessions.get("sessions", [])}
            if thread_id not in session_ids:
                stale = True
        except Exception:
            pass  # Can't verify, assume not stale

    return thread_id, stale


def list_with_status(gw=None):
    """List all agents with their status.

    Returns list of dicts with name, thread_id, title, created_at, updated_at, stale.
    """
    agents = load_agents()
    result = []

    # Get all session IDs once if gateway is provided
    session_ids = None
    if gw is not None:
        try:
            sessions = gw.call_json("sessions.list")
            session_ids = {s.get("session_id") for s in sessions.get("sessions", [])}
        except Exception:
            pass

    for name, entry in sorted(agents["agents"].items()):
        row = {
            "name": name,
            "thread_id": entry.get("thread_id"),
            "title": entry.get("title"),
            "created_at": entry.get("created_at"),
            "updated_at": entry.get("updated_at"),
            "stale": False,
        }
        if session_ids is not None and entry.get("thread_id"):
            if entry["thread_id"] not in session_ids:
                row["stale"] = True
        result.append(row)
    return result
