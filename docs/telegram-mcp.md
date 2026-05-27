# Telegram MCP Integration

This skill can use `chigwell/telegram-mcp` as its preferred private field-intelligence source.

Security default: configure the MCP server with `TELEGRAM_EXPOSED_TOOLS=read-only`. This hides write tools from the MCP client. It does not reduce the underlying Telegram session authority inside the server process, so keep the session string or session file private.

Do not install `uvx telegram-mcp`, `uvx --from telegram-mcp`, or `pip install telegram-mcp` from PyPI. The upstream project documents that the PyPI name is owned by a different project. Install from the GitHub repository or a pinned commit:

```bash
python -m venv .venv-mcp
. .venv-mcp/bin/activate
pip install -r requirements-mcp.txt
```

Minimal environment:

```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef
TELEGRAM_SESSION_STRING=your_session_string
TELEGRAM_EXPOSED_TOOLS=read-only
```

For file-based sessions, use:

```env
TELEGRAM_SESSION_NAME=/secure/path/to/telegram.session
TELEGRAM_EXPOSED_TOOLS=read-only
```

Codex stdio example:

```bash
codex mcp add telegram-mcp -- /absolute/path/to/telegram-mcp
```

If you wrap the command to load secrets from a private env file, keep only the wrapper path in Codex config and keep credentials outside the repository.

Useful read-only tools for this skill:

- `list_chats`
- `get_chat`
- `list_messages`
- `search_messages`
- `get_pinned_messages`
- `get_message_context`
- `list_accounts`

Repeatable refresh:

```bash
python3 scripts/telegram_mcp_refresh.py --days 7 --command /absolute/path/to/telegram-mcp
```
