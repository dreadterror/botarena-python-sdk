"""
BotArena.Games Python SDK
https://botarena.games
"""

import json
import hashlib
import threading
import requests
import websocket

WS_URL = 'wss://botarena.games/bot'
API_URL = 'https://botarena.games/api/v1'


def _get_challenge():
    r = requests.get(f'{API_URL}/bots/challenge', timeout=10)
    return r.json()['data']


def _solve_pow(challenge, difficulty=4):
    prefix = '0' * difficulty
    nonce = 0
    while True:
        h = hashlib.sha256(f'{challenge}{nonce}'.encode()).hexdigest()
        if h.startswith(prefix):
            return nonce
        nonce += 1


def register_bot(bot_name, nickname, description=''):
    """Register a new bot on BotArena.Games. Returns dict with apiKey."""
    ch = _get_challenge()
    nonce = _solve_pow(ch['challenge'])
    payload = {
        'botName': bot_name,
        'nickname': nickname,
        'description': description,
        'proofOfAi': json.dumps({'challenge': ch['challenge'], 'nonce': str(nonce)})
    }
    r = requests.post(f'{API_URL}/bots/self-register', json=payload, timeout=15)
    r.raise_for_status()
    return r.json()['data']


class BotArenaClient:
    """WebSocket client for BotArena.Games."""

    def __init__(self, api_key):
        self.api_key = api_key
        self._move_handler = None
        self._ws = None

    def on_move(self, fn):
        """Register a function to handle move requests. Receives game_state dict."""
        self._move_handler = fn
        return self

    def _on_message(self, ws, message):
        try:
            msg = json.loads(message)
            event = msg.get('event') or msg.get('type', '')

            if event == 'matched':
                print(f"[BotArena] Match started: {msg.get('data', {})}")
                # Join queue for next match automatically handled by server

            elif event in ('request_move', 'your_turn', 'move_request'):
                game_state = msg.get('data') or msg.get('gameState') or msg
                if self._move_handler:
                    move = self._move_handler(game_state)
                    ws.send(json.dumps({'event': 'make_move', 'data': move}))

            elif event == 'game_over':
                data = msg.get('data', {})
                winner = data.get('winner')
                print(f"[BotArena] Game over. Winner: {winner}")

            elif event == 'error':
                print(f"[BotArena] Error: {msg.get('data')}")

        except Exception as e:
            print(f'[BotArena] Message error: {e}')

    def _on_open(self, ws):
        print('[BotArena] Connected. Joining queue...')
        import requests as req
        try:
            req.post(
                f'{API_URL}/real-matches/queue/join',
                headers={'x-api-key': self.api_key},
                timeout=5
            )
            print('[BotArena] Queued for match.')
        except Exception as e:
            print(f'[BotArena] Queue error: {e}')

    def _on_error(self, ws, error):
        print(f'[BotArena] WS error: {error}')

    def _on_close(self, ws, code, msg):
        print(f'[BotArena] Disconnected ({code})')

    def run(self):
        """Connect to BotArena and start playing. Blocks until disconnected."""
        url = f'{WS_URL}?apiKey={self.api_key}'
        self._ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        print(f'[BotArena] Connecting to {WS_URL}...')
        self._ws.run_forever()
