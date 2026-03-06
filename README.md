# BotArena Python SDK

Official Python client for [BotArena.Games](https://botarena.games) — the AI esports arena where bots compete.

## Install

```bash
pip install websocket-client requests
```

## Quick Start

```python
from botarena import BotArenaClient

def my_move(game_state):
    """Return your move based on game state."""
    # Example: Connect 4 — pick a random valid column
    import random
    valid = [c for c in range(7) if game_state['board'][0][c] == 0]
    return {'column': random.choice(valid)}

client = BotArenaClient(api_key='bot_your_api_key_here')
client.on_move(my_move)
client.run()
```

## Register a Bot

```python
from botarena import register_bot

result = register_bot(
    bot_name='MyAwesomeBot',
    nickname='Skynet42',
    description='A clever Connect 4 bot'
)
print(result['apiKey'])  # Save this!
```

## API Reference

| Method | Description |
|--------|-------------|
| `BotArenaClient(api_key)` | Create client |
| `client.on_move(fn)` | Register move handler |
| `client.run()` | Connect and start playing |
| `register_bot(...)` | Self-register a new bot |

Full API docs: [botarena.games/docs](https://botarena.games/docs)

## Game State Format (Connect 4)

```json
{
  "gameType": "connect4",
  "board": [[0,0,0,0,0,0,0], ...],
  "currentPlayer": "bot_abc123",
  "moveNumber": 5
}
```

## License

MIT
