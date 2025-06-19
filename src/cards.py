"""Base card implementation."""
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState

class Card(ABC):
    def __init__(self, card_data: Dict[str, Any]):
        self.id = card_data.get('id')
        self.name = card_data.get('name')
        self.card_type = card_data.get('card_type')
        self.image = card_data.get('image')
        self.rarity = card_data.get('rarity', '')
        self.set_details = card_data.get('set_details', '')
        self.fullart = card_data.get('fullart', 'No') == 'Yes'
        
    @abstractmethod
    def play(self, game_state: 'GameState') -> bool:
        """Play this card according to game rules.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            bool: True if card was played successfully, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name} ({self.card_type})"
