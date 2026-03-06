"""
Example bot: Random Connect 4 player
Register at https://botarena.games/register
"""

import random
from botarena import BotArenaClient

API_KEY = 'bot_your_api_key_here'  # Replace with your bot's API key


def my_move(game_state):
    """Pick a random valid column in Connect 4."""
    board = game_state.get('board', [[]])
    valid_columns = [c for c in range(7) if board[0][c] == 0]
    if not valid_columns:
        return {'column': 0}
    return {'column': random.choice(valid_columns)}


client = BotArenaClient(api_key=API_KEY)
client.on_move(my_move)
client.run()
