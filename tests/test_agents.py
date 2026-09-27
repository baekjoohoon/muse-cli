"""Tests for the agent side-chat workflow."""
import argparse
import json
import os
import sys

import pytest
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from muse_cli import agents as agents_mod
from muse_cli import cli


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect config dir to tmp_path."""
    monkeypatch.setattr(agents_mod, "get_config_dir", lambda: str(tmp_path))
    return tmp_path


@pytest.fixture
def mock_gateway():
    """Create a mock gateway."""
    return MagicMock()


@pytest.fixture
def mock_connect(monkeypatch, mock_gateway):
    """Mock cli.connect and cli.load_config."""
    monkeypatch.setattr(cli, "connect", lambda cfg: mock_gateway)
    monkeypatch.setattr(cli, "load_config", lambda: {
        "cookies_file": "/dev/null", "vm_id": "test", "node_id": "test"
    })
    return mock_gateway


class TestValidateAgentName:
    def test_valid_simple(self):
        assert agents_mod.validate_agent_name("myagent") == "myagent"

    def test_valid_with_numbers(self):
        assert agents_mod.validate_agent_name("agent123") == "agent123"

    def test_valid_with_hyphen(self):
        assert agents_mod.validate_agent_name("my-agent") == "my-agent"

    def test_valid_with_underscore(self):
        assert agents_mod.validate_agent_name("my_agent") == "my_agent"

    def test_case_insensitive(self):
        assert agents_mod.validate_agent_name("MyAgent") == "myagent"

    def test_strips_whitespace(self):
        assert agents_mod.validate_agent_name("  myagent  ") == "myagent"

    def test_max_length(self):
        assert agents_mod.validate_agent_name("a" * 64) == "a" * 64

    def test_too_long(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("a" * 65)

    def test_empty(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("")

    def test_starts_with_hyphen(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("-agent")

    def test_starts_with_underscore(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("_agent")

    def test_contains_space(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("my agent")

    def test_contains_special(self):
        with pytest.raises(ValueError):
            agents_mod.validate_agent_name("my.agent!")


class TestGetConfigDir:
    def test_default(self, monkeypatch):
        monkeypatch.delenv("MUSE_CLI_CONFIG_DIR", raising=False)
        result = agents_mod.get_config_dir()
        assert result == os.path.expanduser("~/.config/muse-cli")

    def test_env_override(self, monkeypatch, tmp_path):
        monkeypatch.setenv("MUSE_CLI_CONFIG_DIR", str(tmp_path))
        result = agents_mod.get_config_dir()
        assert result == str(tmp_path)


class TestAgentsFile:
    def test_path(self, tmp_config):
        path = agents_mod.agents_file()
        assert path == os.path.join(str(tmp_config), "agents.json")


class TestLoadSaveAgents:
    def test_load_nonexistent(self, tmp_config):
        data = agents_mod.load_agents()
        assert data == {"version": 1, "agents": {}}

    def test_save_and_load(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "test": {
                    "thread_id": "thread-123",
                    "title": "Test Agent",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            }
        }
        agents_mod.save_agents_atomic(data)
        loaded = agents_mod.load_agents()
        assert loaded == data

    def test_file_permissions(self, tmp_config):
        data = {"version": 1, "agents": {}}
        agents_mod.save_agents_atomic(data)
        path = agents_mod.agents_file()
        if os.name == "posix":
            mode = os.stat(path).st_mode & 0o777
            assert mode == 0o644

    def test_load_corrupted(self, tmp_config):
        path = agents_mod.agents_file()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write("not json")
        data = agents_mod.load_agents()
        assert data == {"version": 1, "agents": {}}

    def test_load_wrong_shape(self, tmp_config):
        path = agents_mod.agents_file()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump({"wrong": "shape"}, fh)
        data = agents_mod.load_agents()
        assert data == {"version": 1, "agents": {}}


class TestResolveThread:
    def test_unknown_agent(self, tmp_config):
        with pytest.raises(KeyError):
            agents_mod.resolve_thread("nonexistent")

    def test_resolve_existing(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "test": {"thread_id": "thread-123", "title": "Test",
                         "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)
        thread_id, stale = agents_mod.resolve_thread("test")
        assert thread_id == "thread-123"
        assert stale is False

    def test_resolve_stale(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "test": {"thread_id": "thread-123", "title": "Test",
                         "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)
        gw = MagicMock()
        gw.call_json.return_value = {"sessions": [{"session_id": "other-thread"}]}
        thread_id, stale = agents_mod.resolve_thread("test", gw=gw)
        assert thread_id == "thread-123"
        assert stale is True

    def test_resolve_not_stale(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "test": {"thread_id": "thread-123", "title": "Test",
                         "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)
        gw = MagicMock()
        gw.call_json.return_value = {"sessions": [{"session_id": "thread-123"}]}
        thread_id, stale = agents_mod.resolve_thread("test", gw=gw)
        assert thread_id == "thread-123"
        assert stale is False


class TestListWithStatus:
    def test_empty(self, tmp_config):
        result = agents_mod.list_with_status()
        assert result == []

    def test_list_agents(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "agent1": {"thread_id": "t1", "title": "Agent 1",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
                "agent2": {"thread_id": "t2", "title": "Agent 2",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
            }
        }
        agents_mod.save_agents_atomic(data)
        result = agents_mod.list_with_status()
        assert len(result) == 2
        assert result[0]["name"] == "agent1"
        assert result[1]["name"] == "agent2"

    def test_list_with_stale(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "agent1": {"thread_id": "t1", "title": "Agent 1",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
            }
        }
        agents_mod.save_agents_atomic(data)
        gw = MagicMock()
        gw.call_json.return_value = {"sessions": [{"session_id": "other"}]}
        result = agents_mod.list_with_status(gw=gw)
        assert result[0]["stale"] is True

    def test_list_not_stale(self, tmp_config):
        data = {
            "version": 1,
            "agents": {
                "agent1": {"thread_id": "t1", "title": "Agent 1",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
            }
        }
        agents_mod.save_agents_atomic(data)
        gw = MagicMock()
        gw.call_json.return_value = {"sessions": [{"session_id": "t1"}]}
        result = agents_mod.list_with_status(gw=gw)
        assert result[0]["stale"] is False


class TestAgentInit:
    def test_init_new_agent(self, tmp_config, mock_connect, capsys):
        mock_connect.call_json.side_effect = [
            {"session_id": "new-thread-123", "title": "Test Agent"},
        ]

        args = argparse.Namespace(name="testagent", title="Test Agent")
        cli.cmd_agent_init(args)

        data = agents_mod.load_agents()
        assert "testagent" in data["agents"]
        assert data["agents"]["testagent"]["thread_id"] == "new-thread-123"

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["name"] == "testagent"
        assert result["thread_id"] == "new-thread-123"
        assert result["reused"] is False

    def test_init_reuse_existing(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "existing-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "existing-thread"}]}

        args = argparse.Namespace(name="testagent", title="Test")
        cli.cmd_agent_init(args)

        assert mock_connect.call_json.call_count == 1

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["reused"] is True

    def test_init_rebind_stale(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "stale-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.side_effect = [
            {"sessions": [{"session_id": "other-thread"}]},
            {"session_id": "new-thread", "title": "Test"},
        ]

        args = argparse.Namespace(name="testagent", title="Test")
        cli.cmd_agent_init(args)

        data = agents_mod.load_agents()
        assert data["agents"]["testagent"]["thread_id"] == "new-thread"

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["reused"] is False

    def test_init_invalid_name(self, tmp_config, mock_connect, capsys):
        args = argparse.Namespace(name="invalid name!", title="Test")
        with pytest.raises(ValueError):
            cli.cmd_agent_init(args)


class TestAgentList:
    def test_list_empty(self, tmp_config, mock_connect, capsys):
        args = argparse.Namespace()
        cli.cmd_agent_list(args)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result == []

    def test_list_with_agents(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "agent1": {"thread_id": "t1", "title": "Agent 1",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "t1"}]}

        args = argparse.Namespace()
        cli.cmd_agent_list(args)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) == 1
        assert result[0]["name"] == "agent1"
        assert result[0]["stale"] is False

    def test_list_with_stale(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "agent1": {"thread_id": "t1", "title": "Agent 1",
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "other"}]}

        args = argparse.Namespace()
        cli.cmd_agent_list(args)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result[0]["stale"] is True


class TestAgentSend:
    def test_send_unknown_agent(self, tmp_config, mock_connect, capsys):
        args = argparse.Namespace(name="nonexistent", text="hello", wait=0)
        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_agent_send(args)
        assert exc_info.value.code == 2

        captured = capsys.readouterr()
        assert "unknown agent" in captured.err
        assert "agent init" in captured.err

    def test_send_stale_agent(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "stale-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "other"}]}

        args = argparse.Namespace(name="testagent", text="hello", wait=0)
        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_agent_send(args)
        assert exc_info.value.code == 3

        captured = capsys.readouterr()
        assert "stale" in captured.err
        assert "rebind" in captured.err

    def test_send_existing_agent(self, tmp_config, mock_connect, monkeypatch):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "valid-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "valid-thread"}]}

        captured_ns = {}
        def mock_cmd_send(ns):
            captured_ns.update(vars(ns))
        monkeypatch.setattr(cli, "cmd_send", mock_cmd_send)

        args = argparse.Namespace(name="testagent", text="hello", wait=0)
        cli.cmd_agent_send(args)

        assert captured_ns["thread"] == "valid-thread"
        assert captured_ns["text"] == "hello"
        assert captured_ns["wait"] == 0


class TestAgentHistory:
    def test_history_unknown_agent(self, tmp_config, mock_connect, capsys):
        args = argparse.Namespace(name="nonexistent", limit=10, raw=False)
        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_agent_history(args)
        assert exc_info.value.code == 2

        captured = capsys.readouterr()
        assert "unknown agent" in captured.err

    def test_history_stale_agent(self, tmp_config, mock_connect, capsys):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "stale-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "other"}]}

        args = argparse.Namespace(name="testagent", limit=10, raw=False)
        with pytest.raises(SystemExit) as exc_info:
            cli.cmd_agent_history(args)
        assert exc_info.value.code == 3

    def test_history_existing_agent(self, tmp_config, mock_connect, monkeypatch):
        data = {
            "version": 1,
            "agents": {
                "testagent": {"thread_id": "valid-thread", "title": "Test",
                              "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
            }
        }
        agents_mod.save_agents_atomic(data)

        mock_connect.call_json.return_value = {"sessions": [{"session_id": "valid-thread"}]}

        captured_ns = {}
        def mock_cmd_history(ns):
            captured_ns.update(vars(ns))
        monkeypatch.setattr(cli, "cmd_history", mock_cmd_history)

        args = argparse.Namespace(name="testagent", limit=5, raw=True)
        cli.cmd_agent_history(args)

        assert captured_ns["thread"] == "valid-thread"
        assert captured_ns["limit"] == 5
        assert captured_ns["raw"] is True
