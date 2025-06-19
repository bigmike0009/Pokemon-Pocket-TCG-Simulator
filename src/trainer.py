"""Trainer card implementations."""
from typing import Dict, Any, TYPE_CHECKING
from abc import abstractmethod
from .cards import Card

if TYPE_CHECKING:
    from .game_state import GameState

class Trainer(Card):
    def __init__(self, card_data: Dict[str, Any]):
        super().__init__(card_data)
        
        # Convert 'ability' field to match Pokemon card format
        ability = card_data.get('ability')
        if ability:
            if isinstance(ability, dict):
                self.ability = {
                    'name': ability.get('name', 'Effect'),
                    'effect': ability.get('effect', '')
                }
            elif isinstance(ability, str):
                self.ability = {
                    'name': 'Effect',
                    'effect': ability
                }
            else:
                self.ability = {
                    'name': 'No effect',
                    'effect': 'N/A'
                }
        else:
            self.ability = {
                'name': 'No effect',
                'effect': 'N/A'
            }

class Item(Trainer):
    def play(self, game_state: 'GameState') -> bool:
        """Play an item card - can be played multiple times per turn."""
        return game_state.play_item(self)

class Supporter(Trainer):
    def play(self, game_state: 'GameState') -> bool:
        """Play a supporter card - only once per turn."""
        if game_state.supporter_played_this_turn:
            return False
        return game_state.play_supporter(self)

class Tool(Trainer):
    def play(self, game_state: 'GameState') -> bool:
        """Play a tool card - one per Pokemon."""
        return game_state.attach_tool(self)
