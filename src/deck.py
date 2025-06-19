"""Deck implementation."""
from typing import List, Set
from collections import Counter
import random
from .cards import Card
from .pokemon import Pokemon, ElementType

class Deck:
    def __init__(self, cards: List[Card], energy_types: List[ElementType]):
        """Initialize a deck with a list of cards and declared energy types.
        
        Args:
            cards: List of Card objects for the deck
            energy_types: List of ElementType enums (e.g., [ElementType.FIRE, ElementType.WATER])
        
        Raises:
            ValueError: If deck doesn't meet construction requirements
        """
        if not self._validate_deck_size(cards):
            raise ValueError("Deck must contain exactly 20 cards")
            
        if not self._validate_card_copies(cards):
            raise ValueError("Deck cannot contain more than 2 copies of any card with the same name")
            
        if not self._validate_basic_pokemon(cards):
            raise ValueError("Deck must contain at least 1 basic Pokemon")
            
        if not energy_types:
            raise ValueError("Deck must declare at least 1 energy type")
        
        self.cards = cards
        self.energy_types = energy_types
        
    def _validate_deck_size(self, cards: List[Card]) -> bool:
        """Check if deck has exactly 20 cards."""
        return len(cards) == 20
        
    def _validate_card_copies(self, cards: List[Card]) -> bool:
        """Check if deck has no more than 2 copies of any card with same name."""
        name_counts = Counter(card.name for card in cards)
        return all(count <= 2 for count in name_counts.values())
        
    def _validate_basic_pokemon(self, cards: List[Card]) -> bool:
        """Check if deck has at least 1 basic Pokemon."""
        return any(isinstance(card, Pokemon) and card.evolution_type == 'Basic'
                  for card in cards)
                  
    def shuffle(self) -> None:
        """Shuffle the deck."""
        import random
        random.shuffle(self.cards)
        
    def draw(self) -> Card:
        """Draw a card from the top of the deck.
        
        Returns:
            Card: The drawn card
            
        Raises:
            IndexError: If deck is empty
        """
        if not self.cards:
            raise IndexError("Cannot draw from empty deck")
        return self.cards.pop()
    
    def draw_random_energy(self) -> ElementType:
        """Draw a random energy type from the deck's available energy types.
        
        Returns:
            ElementType: A random energy type from this deck's energy_types
        """
        return random.choice(self.energy_types)
        
    def __len__(self) -> int:
        """Get number of cards remaining in deck."""
        return len(self.cards)
